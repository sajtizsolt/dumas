import json
from pathlib import Path

import pytest

from dumas.configuration import Configuration
from dumas.configurationparser import ConfigurationParser


@pytest.fixture
def valid_config_dict() -> dict[str, object]:
    return {
        "bot": {
            "app": 123456789,
            "token": "secret-token-xyz",
        },
        "channel": {
            "sources": [111, 222],
            "target": 333,
        },
        "message": {
            "farewell": "Farewell!",
            "frequency": 15,
            "length": 8,
            "limit": 500,
            "warning": "Warning alert!",
            "welcome": "Hello server!",
        },
    }


def test_verify_configuration_file(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    config = ConfigurationParser.verify_configuration_file(str(config_file))
    assert isinstance(config, Configuration)
    assert config.bot_app == 123456789
    assert config.bot_token == "secret-token-xyz"
    assert config.channel_sources == [111, 222]
    assert config.channel_target == 333
    assert config.message_frequency == 15
    assert config.message_welcome == "Hello server!"


def test_missing_key_raises_key_error(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    del valid_config_dict["message"]
    config_file = tmp_path / "invalid_config.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(KeyError, match="message"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_file_not_found_raises() -> None:
    with pytest.raises(FileNotFoundError):
        ConfigurationParser.verify_configuration_file("/non/existent/path.json")


def test_get_json_masks_token(valid_config_dict: dict[str, object], tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")
    config = ConfigurationParser.verify_configuration_file(str(config_file))

    json_str = ConfigurationParser.get_json(config)
    parsed = json.loads(json_str)
    assert parsed["bot"]["token"] == "Secret token!"


def test_env_token_override(
    tmp_path: Path,
    valid_config_dict: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bot_dict = valid_config_dict["bot"]
    assert isinstance(bot_dict, dict)
    bot_dict["token"] = "ENV"
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    monkeypatch.setenv("DISCORD_TOKEN", "override-token-from-env")
    config = ConfigurationParser.verify_configuration_file(str(config_file))
    assert config.bot_token == "override-token-from-env"
