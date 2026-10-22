import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dumas.argumentparser import Arguments
from dumas.configuration import Configuration
from dumas.main import configure_logger, main


def test_configure_logger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    configure_logger(logging.DEBUG)
    root = logging.getLogger()
    assert root.level == logging.DEBUG
    handler_types = [type(h) for h in root.handlers]
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types


def test_configure_logger_filehandler_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_file_handler(*_args: object, **_kwargs: object) -> logging.Handler:
        raise OSError("Read-only file system")

    monkeypatch.setattr("logging.FileHandler", fail_file_handler)
    configure_logger(logging.INFO)
    root = logging.getLogger()
    assert root.level == logging.INFO
    handler_types = [type(h) for h in root.handlers]
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler not in handler_types


def test_main_config_load_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_args = Arguments(configuration_path="missing.json", logging_level=20)
    monkeypatch.setattr("dumas.main.load_dotenv", lambda: None)
    monkeypatch.setattr("dumas.main.ArgumentParser.verify_arguments", lambda: fake_args)
    monkeypatch.setattr(
        "dumas.main.ConfigurationParser.verify_configuration_file",
        MagicMock(side_effect=FileNotFoundError("Not found")),
    )

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_main_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_args = Arguments(configuration_path="valid.json", logging_level=20)
    fake_config = Configuration(
        bot_app=123,
        bot_token="fake-token",
        channel_sources=(10, 20),
        channel_target=30,
        message_farewell="Farewell",
        message_frequency=1,
        message_length=5,
        message_limit=100,
        message_warning="Warning",
        message_welcome="Welcome",
    )

    mock_run = MagicMock()
    monkeypatch.setattr("dumas.main.load_dotenv", lambda: None)
    monkeypatch.setattr("dumas.main.ArgumentParser.verify_arguments", lambda: fake_args)
    monkeypatch.setattr(
        "dumas.main.ConfigurationParser.verify_configuration_file",
        lambda _: fake_config,
    )
    monkeypatch.setattr("dumas.main.Dumas.run", mock_run)

    main()
    mock_run.assert_called_once_with("fake-token", log_handler=None)


def test_main_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_args = Arguments(configuration_path="valid.json", logging_level=20)
    fake_config = Configuration(
        bot_app=123,
        bot_token="fake-token",
        channel_sources=(10, 20),
        channel_target=30,
        message_farewell="Farewell",
        message_frequency=1,
        message_length=5,
        message_limit=100,
        message_warning="Warning",
        message_welcome="Welcome",
    )

    monkeypatch.setattr("dumas.main.load_dotenv", lambda: None)
    monkeypatch.setattr("dumas.main.ArgumentParser.verify_arguments", lambda: fake_args)
    monkeypatch.setattr(
        "dumas.main.ConfigurationParser.verify_configuration_file",
        lambda _: fake_config,
    )
    monkeypatch.setattr(
        "dumas.main.Dumas.run",
        MagicMock(side_effect=KeyboardInterrupt),
    )

    # Should catch KeyboardInterrupt and return normally without error
    main()
