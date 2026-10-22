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
    assert config.channel_sources == (111, 222)
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


def test_invalid_frequency_raises(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    msg_dict = valid_config_dict["message"]
    assert isinstance(msg_dict, dict)
    msg_dict["frequency"] = 0
    config_file = tmp_path / "invalid_freq.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"message\.frequency"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_invalid_limit_raises(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    msg_dict = valid_config_dict["message"]
    assert isinstance(msg_dict, dict)
    msg_dict["limit"] = -1
    config_file = tmp_path / "invalid_limit.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"message\.limit"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_invalid_length_raises(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    msg_dict = valid_config_dict["message"]
    assert isinstance(msg_dict, dict)
    msg_dict["length"] = 0
    config_file = tmp_path / "invalid_length.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"message\.length"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_invalid_channel_sources_items_raises(
    tmp_path: Path, valid_config_dict: dict[str, object]
) -> None:
    chan_dict = valid_config_dict["channel"]
    assert isinstance(chan_dict, dict)
    chan_dict["sources"] = ["invalid_id"]
    config_file = tmp_path / "invalid_items.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"channel\.sources must be integer IDs"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_empty_sources_raises(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    chan_dict = valid_config_dict["channel"]
    assert isinstance(chan_dict, dict)
    chan_dict["sources"] = []
    config_file = tmp_path / "empty_sources.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"channel\.sources"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_empty_token_raises(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    bot_dict = valid_config_dict["bot"]
    assert isinstance(bot_dict, dict)
    bot_dict["token"] = ""
    config_file = tmp_path / "empty_token.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"bot\.token"):
        ConfigurationParser.verify_configuration_file(str(config_file))


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


def test_invalid_bot_app_raises(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    bot_dict = valid_config_dict["bot"]
    assert isinstance(bot_dict, dict)
    bot_dict["app"] = "not_an_int"
    config_file = tmp_path / "invalid_app.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"bot\.app must be a valid integer"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_invalid_channel_target_raises(
    tmp_path: Path, valid_config_dict: dict[str, object]
) -> None:
    chan_dict = valid_config_dict["channel"]
    assert isinstance(chan_dict, dict)
    chan_dict["target"] = "not_an_int"
    config_file = tmp_path / "invalid_target.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"channel\.target must be a valid integer"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_read_and_write_configuration_roundtrip(
    tmp_path: Path, valid_config_dict: dict[str, object]
) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")
    config = ConfigurationParser.read_configuration(str(config_file))

    out_file = tmp_path / "written_config.json"
    ConfigurationParser.write_configuration_to_file(str(out_file), config)
    reloaded = ConfigurationParser.read_configuration(str(out_file))
    assert reloaded == config


def test_channel_sources_deduplicated(tmp_path: Path, valid_config_dict: dict[str, object]) -> None:
    chan_dict = valid_config_dict["channel"]
    assert isinstance(chan_dict, dict)
    chan_dict["sources"] = [111, 222, 111, 333, 222]
    config_file = tmp_path / "dedup_sources.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    config = ConfigurationParser.verify_configuration_file(str(config_file))
    assert config.channel_sources == (111, 222, 333)


def test_non_positive_ids_raise_value_error(
    tmp_path: Path, valid_config_dict: dict[str, object]
) -> None:
    bot_dict = valid_config_dict["bot"]
    assert isinstance(bot_dict, dict)
    bot_dict["app"] = 0
    config_file = tmp_path / "zero_app.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"bot\.app must be a positive integer"):
        ConfigurationParser.verify_configuration_file(str(config_file))

    bot_dict["app"] = 12345
    chan_dict = valid_config_dict["channel"]
    assert isinstance(chan_dict, dict)
    chan_dict["target"] = -1
    config_file2 = tmp_path / "negative_target.json"
    config_file2.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"channel\.target must be a positive integer"):
        ConfigurationParser.verify_configuration_file(str(config_file2))

    chan_dict["target"] = 12345
    chan_dict["sources"] = [10, -5]
    config_file3 = tmp_path / "negative_source.json"
    config_file3.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"channel\.sources must be positive integer"):
        ConfigurationParser.verify_configuration_file(str(config_file3))


def test_placeholder_token_raises_value_error(
    tmp_path: Path, valid_config_dict: dict[str, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    bot_dict = valid_config_dict["bot"]
    assert isinstance(bot_dict, dict)
    bot_dict["token"] = "YOUR_TOKEN_HERE"
    config_file = tmp_path / "placeholder_token.json"
    config_file.write_text(json.dumps(valid_config_dict), encoding="utf-8")

    with pytest.raises(ValueError, match=r"placeholders"):
        ConfigurationParser.verify_configuration_file(str(config_file))


def test_non_dict_root_json_raises_value_error(tmp_path: Path) -> None:
    list_config = tmp_path / "list_config.json"
    list_config.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(TypeError, match=r"Configuration file root must be a JSON object"):
        ConfigurationParser.verify_configuration_file(str(list_config))

    str_config = tmp_path / "str_config.json"
    str_config.write_text('"just a string"', encoding="utf-8")
    with pytest.raises(TypeError, match=r"Configuration file root must be a JSON object"):
        ConfigurationParser.verify_configuration_file(str(str_config))
