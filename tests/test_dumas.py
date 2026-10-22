from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from dumas.configuration import Configuration
from dumas.dumas import DISCORD_MAX_MESSAGE_LENGTH, Dumas
from dumas.message import Message


@pytest.fixture
def test_config() -> Configuration:
    return Configuration(
        bot_app=123,
        bot_token="dummy-token",
        channel_sources=(10, 20),
        channel_target=30,
        message_farewell="Farewell all!",
        message_frequency=1,
        message_length=5,
        message_limit=100,
        message_warning="Warning!",
        message_welcome="Welcome!",
    )


def create_mock_message(
    content: str,
    *,
    author_bot: bool = False,
    channel_id: int = 10,
) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    msg.author.bot = author_bot
    msg.author.id = 999
    msg.channel.id = channel_id
    return msg


def test_get_author_id_from_message(test_config: Configuration) -> None:
    bot = Dumas(test_config)

    # Standard numeric ID
    assert bot.get_author_id_from_message(create_mock_message("&random 12345")) == 12345

    # Mention formats
    assert bot.get_author_id_from_message(create_mock_message("&random <@12345>")) == 12345
    assert bot.get_author_id_from_message(create_mock_message("&random <@!12345>")) == 12345

    # Extra whitespace
    assert bot.get_author_id_from_message(create_mock_message("&start    555")) == 555

    # No argument or non-numeric
    assert bot.get_author_id_from_message(create_mock_message("&random")) is None
    assert bot.get_author_id_from_message(create_mock_message("&random abc")) is None
    assert bot.get_author_id_from_message(create_mock_message("not a command")) is None


@pytest.mark.asyncio
async def test_send_message_truncation_and_mentions(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    mock_channel = AsyncMock()
    bot.target_channel = mock_channel

    # Regular long text truncation
    long_text = "x" * 3000
    await bot.send_message(long_text)
    sent_text = mock_channel.send.call_args[0][0]
    assert len(sent_text) <= DISCORD_MAX_MESSAGE_LENGTH
    assert sent_text.endswith("...")
    # Verify allowed_mentions suppression
    allowed_mentions = mock_channel.send.call_args.kwargs["allowed_mentions"]
    assert not allowed_mentions.everyone
    assert not allowed_mentions.users
    assert not allowed_mentions.roles

    # Code block truncation
    mock_channel.reset_mock()
    code_text = "```json\n" + ("a" * 3000) + "\n```"
    await bot.send_message(code_text)
    code_sent = mock_channel.send.call_args[0][0]
    assert len(code_sent) <= DISCORD_MAX_MESSAGE_LENGTH
    assert code_sent.endswith("...\n```")


@pytest.mark.asyncio
async def test_send_random_message_empty(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    mock_channel = AsyncMock()
    bot.target_channel = mock_channel

    # Should send feedback when no messages exist
    await bot.send_random_message(author_id=None)
    mock_channel.send.assert_awaited_once()
    assert "No messages have been archived" in mock_channel.send.call_args[0][0]


@pytest.mark.asyncio
async def test_send_random_message_unknown_author(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    mock_channel = AsyncMock()
    bot.target_channel = mock_channel
    bot.messages = {100: [Message(author_id=100, content="Hello 100")]}

    await bot.send_random_message(author_id=999)
    mock_channel.send.assert_awaited_once()
    assert "No archived messages found for user 999" in mock_channel.send.call_args[0][0]


@pytest.mark.asyncio
async def test_send_random_message_specific_author(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    mock_channel = AsyncMock()
    bot.target_channel = mock_channel

    bot.messages = {
        100: [Message(author_id=100, content="Hello from 100")],
        200: [Message(author_id=200, content="Hello from 200")],
    }

    await bot.send_random_message(author_id=100)
    mock_channel.send.assert_awaited_once()
    assert "Hello from 100" in mock_channel.send.call_args[0][0]


@pytest.mark.asyncio
async def test_on_message_exact_matching_and_casing(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.show_help = AsyncMock()  # type: ignore[method-assign]
    bot.send_messages_continuously = AsyncMock()  # type: ignore[method-assign]

    # Mobile casing should trigger help
    await bot.on_message(create_mock_message("&Help"))
    bot.show_help.assert_awaited_once()

    # Prefix overlap should NOT trigger &start
    await bot.on_message(create_mock_message("&starting something"))
    bot.send_messages_continuously.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_bot_and_channel_filtering(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.show_help = AsyncMock()  # type: ignore[method-assign]

    # Bot author ignored
    await bot.on_message(create_mock_message("&help", author_bot=True))
    bot.show_help.assert_not_called()

    # Wrong channel ignored
    await bot.on_message(create_mock_message("&help", channel_id=9999))
    bot.show_help.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_invalid_arguments_feedback(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.send_message = AsyncMock()  # type: ignore[method-assign]

    # Non-numeric author argument
    await bot.on_message(create_mock_message("&random invalid_id"))
    bot.send_message.assert_awaited_once()
    assert "Invalid author ID or mention: 'invalid_id'" in bot.send_message.call_args[0][0]

    # Too many arguments
    bot.send_message.reset_mock()
    await bot.on_message(create_mock_message("&start 123 extra_arg"))
    bot.send_message.assert_awaited_once()
    assert "Too many arguments provided" in bot.send_message.call_args[0][0]


@pytest.mark.asyncio
async def test_on_ready_idempotency(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.read_message_history = AsyncMock()  # type: ignore[method-assign]
    bot.send_message = AsyncMock()  # type: ignore[method-assign]
    bot.get_channel = MagicMock(return_value=AsyncMock(spec=discord.abc.Messageable))  # type: ignore[method-assign]

    # First call
    await bot.on_ready()
    assert bot._is_ready is True
    bot.read_message_history.assert_awaited_once()

    # Second call (reconnect) should return early
    await bot.on_ready()
    bot.read_message_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_on_ready_inaccessible_target_channel_closes(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.read_message_history = AsyncMock()  # type: ignore[method-assign]
    bot.get_channel = MagicMock(return_value=None)  # type: ignore[method-assign]
    bot.fetch_channel = AsyncMock(return_value=None)  # type: ignore[method-assign]
    bot.close = AsyncMock()  # type: ignore[method-assign]

    await bot.on_ready()
    bot.close.assert_awaited_once()
    assert bot.target_channel is None


@pytest.mark.asyncio
async def test_read_channel_history_forbidden(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    mock_channel = MagicMock(spec=discord.abc.Messageable)
    mock_response = MagicMock()
    mock_response.status = 403
    mock_response.reason = "Forbidden"
    mock_channel.history = MagicMock(side_effect=discord.Forbidden(mock_response, "Forbidden"))
    bot.get_channel = MagicMock(return_value=mock_channel)  # type: ignore[method-assign]

    res = await bot._read_channel_history(10)
    assert res == {}


@pytest.mark.asyncio
async def test_close_farewell(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    mock_channel = AsyncMock()
    bot.target_channel = mock_channel
    bot.send_message = AsyncMock()  # type: ignore[method-assign]

    # Close should send farewell
    await bot.close()
    bot.send_message.assert_awaited_with(test_config.message_farewell)


@pytest.mark.asyncio
async def test_read_channel_history_non_messageable(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    non_msg_channel = MagicMock()  # Does NOT spec discord.abc.Messageable
    bot.get_channel = MagicMock(return_value=non_msg_channel)  # type: ignore[method-assign]

    res = await bot._read_channel_history(10)
    assert res == {}


@pytest.mark.asyncio
async def test_read_message_history_gather_handles_exception(test_config: Configuration) -> None:
    bot = Dumas(test_config)

    async def fake_read(channel_id: int) -> dict[int, list[Message]]:
        if channel_id == 10:
            return {100: [Message(author_id=100, content="message 100")]}
        raise RuntimeError("Network error on channel 20")

    bot._read_channel_history = AsyncMock(side_effect=fake_read)  # type: ignore[method-assign]
    await bot.read_message_history()
    assert 100 in bot.messages
    assert len(bot.messages[100]) == 1
    assert bot._available_authors == (100,)


@pytest.mark.asyncio
async def test_on_message_get_config_alias(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.show_configuration = AsyncMock()  # type: ignore[method-assign]

    await bot.on_message(create_mock_message("&get-config"))
    bot.show_configuration.assert_awaited_once()


@pytest.mark.asyncio
async def test_continuous_loop_exception_resets_task(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.send_random_message = AsyncMock(side_effect=RuntimeError("API crash"))  # type: ignore[method-assign]
    bot.send_message = AsyncMock()  # type: ignore[method-assign]

    task = Dumas._continuous_loop(bot, None)
    await task
    assert bot._sending_task is None
    bot.send_message.assert_awaited_with(
        "Continuous message sending encountered an error and stopped."
    )


@pytest.mark.asyncio
async def test_continuous_methods_aliases(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    assert bot.send_messages_continously == bot.send_messages_continuously
    assert bot.stop_sending_messages_continously == bot.stop_sending_messages_continuously


@pytest.mark.asyncio
async def test_send_messages_continuously_no_messages_aborts(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.send_message = AsyncMock()  # type: ignore[method-assign]

    # Specific author with no messages
    await bot.send_messages_continuously(999)
    assert bot._sending_task is None
    bot.send_message.assert_awaited_with("No archived messages found for user 999.")

    # No authors archived in server
    bot.send_message.reset_mock()
    bot._available_authors = ()
    await bot.send_messages_continuously(None)
    assert bot._sending_task is None
    bot.send_message.assert_awaited_with("No messages have been archived yet.")


@pytest.mark.asyncio
async def test_read_channel_history_ignores_bots_and_system_events(
    test_config: Configuration,
) -> None:
    bot = Dumas(test_config)

    # 1. Normal user message
    user_msg = MagicMock()
    user_msg.author.bot = False
    user_msg.author.id = 500
    user_msg.type = discord.MessageType.default
    user_msg.content = "Valid long message from user"

    # 2. Bot message
    bot_msg = MagicMock()
    bot_msg.author.bot = True
    bot_msg.author.id = 600
    bot_msg.type = discord.MessageType.default
    bot_msg.content = "Automated announcement from bot"

    # 3. System event message (e.g. pinned message)
    sys_msg = MagicMock()
    sys_msg.author.bot = False
    sys_msg.author.id = 500
    sys_msg.type = discord.MessageType.pins_add
    sys_msg.content = "Pinned a message to this channel"

    async def async_history(*_args: object, **_kwargs: object):  # noqa: ANN202
        for m in [user_msg, bot_msg, sys_msg]:
            yield m

    mock_channel = MagicMock(spec=discord.abc.Messageable)
    mock_channel.history = async_history
    bot.get_channel = MagicMock(return_value=mock_channel)  # type: ignore[method-assign]

    res = await bot._read_channel_history(10)
    assert 500 in res
    assert len(res[500]) == 1
    assert res[500][0].content == "Valid long message from user"
    assert 600 not in res


@pytest.mark.asyncio
async def test_show_help_mentions_get_config_alias(test_config: Configuration) -> None:
    bot = Dumas(test_config)
    bot.send_message = AsyncMock()  # type: ignore[method-assign]

    await bot.show_help()
    bot.send_message.assert_awaited_once()
    assert "alias: &get-config" in bot.send_message.call_args[0][0]
