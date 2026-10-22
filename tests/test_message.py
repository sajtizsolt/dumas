import pytest

from dumas.configuration import Configuration
from dumas.message import Message


def sample_configuration() -> Configuration:
    return Configuration(
        bot_app=123456789,
        bot_token="test-token",
        channel_sources=(111, 222),
        channel_target=333,
        message_farewell="Goodbye!",
        message_frequency=5,
        message_length=10,
        message_limit=1000,
        message_warning="Warning!",
        message_welcome="Welcome!",
    )


def test_relevant_message() -> None:
    config = sample_configuration()
    msg = Message(author_id=987654321, content="This is a long enough message to be relevant.")
    assert msg.is_relevant(config) is True


def test_short_message_is_filtered() -> None:
    config = sample_configuration()
    msg = Message(author_id=987654321, content="short")
    assert msg.is_relevant(config) is False


def test_bot_app_message_is_filtered() -> None:
    config = sample_configuration()
    msg = Message(author_id=config.bot_app, content="This is sent by the bot app itself!")
    assert msg.is_relevant(config) is False


def test_zero_width_prefix_is_filtered() -> None:
    config = sample_configuration()
    for prefix in ["\u200b", "\u200d", "\ufeff"]:
        msg = Message(author_id=987654321, content=prefix + "Some message content here")
        assert msg.is_relevant(config) is False


def test_groovy_commands_are_filtered() -> None:
    config = sample_configuration()
    for cmd in ["-p https://youtube.com/watch?v=123", "-skip", "-loop", "-dc"]:
        msg = Message(author_id=987654321, content=cmd)
        assert msg.is_relevant(config) is False


def test_dumas_commands_are_filtered() -> None:
    config = sample_configuration()
    for cmd in ["&help", "&start 123", "&stop", "&random", "&show-config"]:
        msg = Message(author_id=987654321, content=cmd)
        assert msg.is_relevant(config) is False


def test_commands_with_whitespace_and_case_are_filtered() -> None:
    config = sample_configuration()
    assert Message(author_id=987654321, content="   &help").is_relevant(config) is False
    assert Message(author_id=987654321, content="  &Start 123").is_relevant(config) is False
    assert Message(author_id=987654321, content=" -P youtube.com").is_relevant(config) is False


def test_message_frozen_immutability() -> None:
    msg = Message(author_id=123, content="immutable content")
    with pytest.raises(AttributeError):
        msg.content = "mutated"  # type: ignore[misc]


def test_messages_starting_with_command_substrings_are_kept() -> None:
    config = sample_configuration()
    valid_contents = [
        "-photo from our vacation",
        "-priority task list here",
        "&starting today at noon",
        "&stopping is not an option",
    ]
    for text in valid_contents:
        assert Message(author_id=987654321, content=text).is_relevant(config) is True
