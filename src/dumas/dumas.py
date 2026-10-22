from __future__ import annotations

import asyncio
import contextlib
import logging
import random
import time
from typing import TYPE_CHECKING, Any

import discord
from discord import Client

from .configurationparser import ConfigurationParser
from .message import Message

if TYPE_CHECKING:
    from .configuration import Configuration

logger = logging.getLogger(__name__)

HELP = """```
Usage:
  &help               - show this help page
  &start [author_id]  - start sending messages continuously (from the specified user)
  &stop               - stop sending messages continuously
  &random [author_id] - send a random message once (from the specified user)
  &show-config        - show active configuration (alias: &get-config)
```"""

DISCORD_MAX_MESSAGE_LENGTH = 2000
COMMAND_WITH_ARG_PARTS = 2
ALLOWED_MESSAGE_TYPES: frozenset[discord.MessageType] = frozenset(
    {
        discord.MessageType.default,
        discord.MessageType.reply,
        discord.MessageType.thread_starter_message,
    }
)


class Dumas(Client):
    def __init__(self, configuration: Configuration, **options: Any) -> None:  # noqa: ANN401
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, **options)

        self.configuration = configuration
        self.messages: dict[int, list[Message]] = {}
        self.target_channel: discord.abc.Messageable | None = None
        self._is_ready = False
        self._sending_task: asyncio.Task[None] | None = None
        self._available_authors: tuple[int, ...] = ()
        self._allowed_channel_ids = frozenset(configuration.channel_sources) | {
            configuration.channel_target,
        }

    async def on_ready(self) -> None:
        if self._is_ready:
            logger.info("Dumas reconnected.")
            return

        self._is_ready = True
        logger.info("Dumas is ready.")
        await self.read_message_history()
        channel = self.get_channel(self.configuration.channel_target)
        if channel is None:
            try:
                channel = await self.fetch_channel(self.configuration.channel_target)
            except discord.DiscordException:
                logger.exception(
                    "Could not find target channel %s", self.configuration.channel_target
                )
        if not isinstance(channel, discord.abc.Messageable):
            logger.critical(
                "Target channel %s is not accessible or not messageable. Shutting down.",
                self.configuration.channel_target,
            )
            await self.close()
            return

        self.target_channel = channel
        await self.send_message(self.configuration.message_welcome)

    async def _read_channel_history(self, channel_id: int) -> dict[int, list[Message]]:
        channel: Any = self.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.fetch_channel(channel_id)
            except discord.DiscordException as err:
                logger.warning("Could not access channel %s: %s", channel_id, err)
                return {}

        if not isinstance(channel, discord.abc.Messageable):
            logger.warning("Channel %s does not support message history.", channel_id)
            return {}

        collected: dict[int, list[Message]] = {}
        try:
            async for msg in channel.history(limit=self.configuration.message_limit):
                if msg.author.bot or msg.type not in ALLOWED_MESSAGE_TYPES:
                    continue
                message = Message(author_id=msg.author.id, content=msg.content)
                if message.is_relevant(self.configuration):
                    collected.setdefault(message.author_id, []).append(message)
        except discord.Forbidden:
            logger.warning("Missing permissions to read message history in channel %s.", channel_id)
        except discord.DiscordException as err:
            logger.warning("Failed to fetch messages for channel %s: %s", channel_id, err)
        return collected

    async def read_message_history(self) -> None:
        start = time.time()
        logger.info("Starting to read message history...")
        results = await asyncio.gather(
            *(
                self._read_channel_history(channel_id)
                for channel_id in self.configuration.channel_sources
            ),
            return_exceptions=True,
        )
        collected: dict[int, list[Message]] = {}
        for res in results:
            if isinstance(res, BaseException):
                logger.error("Unexpected error reading channel history: %s", res, exc_info=res)
            else:
                for author_id, msgs in res.items():
                    collected.setdefault(author_id, []).extend(msgs)
        self.messages = collected
        self._available_authors = tuple(collected.keys())
        logger.info("Finished reading message history!")
        logger.info("Elapsed time: %.2f seconds", time.time() - start)

    async def send_message(self, message: object) -> None:
        zero_width_prefix = "\u200b\u200d\ufeff"
        text = str(message)
        payload = zero_width_prefix + text
        if len(payload) > DISCORD_MAX_MESSAGE_LENGTH:
            if text.strip().startswith("```"):
                payload = payload[: DISCORD_MAX_MESSAGE_LENGTH - 7] + "...\n```"
            else:
                payload = payload[: DISCORD_MAX_MESSAGE_LENGTH - 3] + "..."

        if self.target_channel:
            try:
                await self.target_channel.send(
                    payload,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            except discord.DiscordException:
                logger.exception("Failed to send message")
        else:
            logger.error("Target channel is not available; cannot send message.")

    async def _validate_command_args(self, command: str, parts: list[str]) -> bool:
        if command in ("&start", "&random"):
            if len(parts) > COMMAND_WITH_ARG_PARTS:
                await self.send_message(
                    f"Too many arguments provided. Usage: `{command} [author_id]`",
                )
                return False
            if (
                len(parts) == COMMAND_WITH_ARG_PARTS
                and self.get_author_id_from_parts(parts) is None
            ):
                await self.send_message(
                    f"Invalid author ID or mention: '{parts[1]}'. Usage: `{command} [author_id]`",
                )
                return False
        return True

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.channel.id not in self._allowed_channel_ids:
            return

        parts = message.content.strip().split()
        if not parts:
            return

        command = parts[0].lower()
        if not await self._validate_command_args(command, parts):
            return

        author_id = self.get_author_id_from_parts(parts)

        if author_id == self.configuration.bot_app:
            await self.send_message(self.configuration.message_warning)
        elif command == "&help":
            await self.show_help()
        elif command == "&start":
            await self.send_messages_continuously(author_id)
        elif command == "&stop":
            await self.stop_sending_messages_continuously()
        elif command == "&random":
            await self.send_random_message(author_id)
        elif command in ("&show-config", "&get-config"):
            await self.show_configuration()

    @staticmethod
    def get_author_id_from_parts(parts: list[str]) -> int | None:
        if len(parts) == COMMAND_WITH_ARG_PARTS:
            raw_id = parts[1].removeprefix("<@").removeprefix("!").removesuffix(">")
            if raw_id.isnumeric():
                return int(raw_id)
        return None

    @staticmethod
    def get_author_id_from_message(message: discord.Message) -> int | None:
        return Dumas.get_author_id_from_parts(message.content.strip().split())

    async def show_help(self) -> None:
        logger.info("Showing help.")
        await self.send_message(HELP)

    async def send_messages_continuously(self, author_id: int | None) -> None:
        if self._sending_task and not self._sending_task.done():
            logger.warning("Message sending task is already running.")
            await self.send_message("Continuous message sending is already active!")
            return

        if author_id is not None:
            if author_id not in self.messages or not self.messages[author_id]:
                logger.warning("Author %s has no messages available.", author_id)
                await self.send_message(f"No archived messages found for user {author_id}.")
                return
        elif not self._available_authors:
            logger.warning("No authors found in message history.")
            await self.send_message("No messages have been archived yet.")
            return

        logger.info("Starting to send messages continuously.")
        self._sending_task = asyncio.create_task(self._continuous_loop(author_id))

    send_messages_continously = send_messages_continuously

    async def _continuous_loop(self, author_id: int | None) -> None:
        try:
            while True:
                await self.send_random_message(author_id)
                await asyncio.sleep(self.configuration.message_frequency)
        except asyncio.CancelledError:
            logger.info("Continuous message sending cancelled.")
        except Exception:
            logger.exception("Continuous message sending loop crashed unexpectedly.")
            await self.send_message("Continuous message sending encountered an error and stopped.")
        finally:
            self._sending_task = None

    async def _cancel_sending_task(self) -> None:
        if self._sending_task and not self._sending_task.done():
            self._sending_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._sending_task
        self._sending_task = None

    async def stop_sending_messages_continuously(self) -> None:
        if self._sending_task and not self._sending_task.done():
            logger.info("Stopping continuous message sending.")
            await self._cancel_sending_task()
            await self.send_message("Stopped continuous message sending.")
        else:
            await self.send_message("Continuous message sending is not currently active.")

    stop_sending_messages_continously = stop_sending_messages_continuously

    async def send_random_message(self, author_id: int | None) -> None:
        logger.info("Sending a random message.")
        if author_id is not None:
            if author_id not in self.messages or not self.messages[author_id]:
                logger.warning("Author %s has no messages available.", author_id)
                await self.send_message(f"No archived messages found for user {author_id}.")
                return
            chosen_author = author_id
        else:
            if not self._available_authors:
                logger.warning("No authors found in message history.")
                await self.send_message("No messages have been archived yet.")
                return
            chosen_author = random.choice(self._available_authors)

        messages = self.messages.get(chosen_author)
        if not messages:
            return

        chosen_message = random.choice(messages)
        await self.send_message(chosen_message.content)

    async def show_configuration(self) -> None:
        logger.info("Showing configuration.")
        config_json = ConfigurationParser.get_json(self.configuration)
        await self.send_message(f"```json\n{config_json}\n```")

    async def close(self) -> None:
        await self._cancel_sending_task()

        if self.target_channel and self.configuration.message_farewell:
            try:
                await self.send_message(self.configuration.message_farewell)
            except discord.DiscordException:
                logger.exception("Failed to send farewell message on shutdown.")
        await super().close()
