from __future__ import annotations

import asyncio
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
  &show-config        - show active configuration
```"""


COMMAND_WITH_ARG_PARTS = 2


class Dumas(Client):
    def __init__(self, configuration: Configuration, **options: Any) -> None:  # noqa: ANN401
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, **options)

        self.authors: list[int] = []
        self.configuration = configuration
        self.messages: dict[int, list[Message]] = {}
        self.sending_messages = False
        self.target_channel: Any = None

    async def on_ready(self) -> None:
        logger.info("Dumas is ready.")
        await self.read_message_history()
        self.target_channel = self.get_channel(self.configuration.channel_target)
        if self.target_channel is None:
            try:
                self.target_channel = await self.fetch_channel(self.configuration.channel_target)
            except discord.DiscordException:
                logger.exception(
                    "Could not find target channel %s", self.configuration.channel_target
                )
        await self.send_message(self.configuration.message_welcome)

    async def read_message_history(self) -> None:
        start = time.time()
        logger.info("Starting to read message history...")
        for channel_id in self.configuration.channel_sources:
            channel: Any = self.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await self.fetch_channel(channel_id)
                except discord.DiscordException as err:
                    logger.warning("Could not access channel %s: %s", channel_id, err)
                    continue

            if not hasattr(channel, "history"):
                logger.warning("Channel %s does not support message history.", channel_id)
                continue

            async for msg in channel.history(limit=self.configuration.message_limit):
                message = Message(author_id=msg.author.id, content=msg.content)
                if message.is_relevant(self.configuration):
                    if message.author_id not in self.authors:
                        self.authors.append(message.author_id)
                        self.messages[message.author_id] = []
                    self.messages[message.author_id].append(message)

        logger.info("Finished reading message history!")
        logger.info("Elapsed time: %.2f seconds", time.time() - start)

    async def send_message(self, message: object) -> None:
        zero_width_prefix = "\u200b\u200d\ufeff"
        if self.target_channel:
            await self.target_channel.send(zero_width_prefix + str(message))
        else:
            logger.error("Target channel is not available; cannot send message.")

    async def on_message(self, message: discord.Message) -> None:
        logger.info("Someone sent a message.")
        author_id = await self.get_author_id_from_message(message)
        if author_id == self.configuration.bot_app:
            await self.send_message(self.configuration.message_warning)
        elif message.content.startswith("&help"):
            await self.show_help()
        elif message.content.startswith("&start"):
            await self.send_messages_continously(author_id)
        elif message.content.startswith("&stop"):
            await self.stop_sending_messages_continously()
        elif message.content.startswith("&random"):
            await self.send_random_message(author_id)
        elif message.content.startswith("&show-config"):
            await self.show_configuration()

    async def get_author_id_from_message(self, message: discord.Message) -> int | None:
        if message.content.startswith("&"):
            parts = message.content.split(" ")
            if len(parts) == COMMAND_WITH_ARG_PARTS and parts[1].isnumeric():
                return int(parts[1])
        return None

    async def show_help(self) -> None:
        logger.info("Showing help.")
        await self.send_message(HELP)

    async def send_messages_continously(self, author_id: int | None) -> None:
        logger.info("Starting to send messages continuously.")
        self.sending_messages = True
        while self.sending_messages:
            await self.send_random_message(author_id)
            await asyncio.sleep(self.configuration.message_frequency)

    async def stop_sending_messages_continously(self) -> None:
        logger.info("Stopping to send messages continuously.")
        self.sending_messages = False

    async def send_random_message(self, author_id: int | None) -> None:
        logger.info("Sending a random message.")
        if author_id is not None:
            if author_id not in self.messages or not self.messages[author_id]:
                logger.warning("Author %s has no messages available.", author_id)
                return
            chosen_author = author_id
        else:
            if not self.authors:
                logger.warning("No authors found in message history.")
                return
            chosen_author = random.choice(self.authors)

        if not self.messages.get(chosen_author):
            return

        chosen_message = random.choice(self.messages[chosen_author])
        await self.send_message(chosen_message.content)

    async def show_configuration(self) -> None:
        logger.info("Showing configuration.")
        config_json = ConfigurationParser.get_json(self.configuration)
        await self.send_message(f"```json\n{config_json}\n```")
