import json
import os
from pathlib import Path

from .configuration import Configuration


class ConfigurationParser:
    MISSING_KEY_MESSAGE = "Configuration file does not contain the following key: {}"

    @staticmethod
    def get_value_if_key_exists(dictionary: dict[str, object], key_with_dots: str) -> object:
        keys = key_with_dots.split(".")
        current: object = dictionary
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                raise KeyError(ConfigurationParser.MISSING_KEY_MESSAGE.format(key_with_dots))
        return current

    @staticmethod
    def _parse_positive_int(data: dict[str, object], key: str) -> int:
        val = int(str(ConfigurationParser.get_value_if_key_exists(data, key)))
        if val <= 0:
            raise ValueError(f"{key} must be greater than 0")
        return val

    @staticmethod
    def _parse_id(data: dict[str, object], key: str, entity_name: str) -> int:
        raw = ConfigurationParser.get_value_if_key_exists(data, key)
        try:
            val = int(str(raw))
        except (ValueError, TypeError) as err:
            raise ValueError(f"{key} must be a valid integer {entity_name}: {err}") from err
        if val <= 0:
            raise ValueError(f"{key} must be a positive integer {entity_name}")
        return val

    @staticmethod
    def verify_configuration_file(configuration_file_path: str) -> Configuration:
        config_path = Path(configuration_file_path)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {configuration_file_path}")

        with config_path.open(encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise TypeError(
                f"Configuration file root must be a JSON object: {configuration_file_path}",
            )

        raw_token = str(ConfigurationParser.get_value_if_key_exists(data, "bot.token"))
        env_token = os.getenv("DISCORD_TOKEN")
        if env_token and (not raw_token or raw_token in ("ENV", "YOUR_TOKEN_HERE")):
            bot_token = env_token
        else:
            bot_token = raw_token

        if not bot_token or bot_token in ("ENV", "YOUR_TOKEN_HERE"):
            raise ValueError(
                "bot.token must not be empty or contain placeholders ('ENV', 'YOUR_TOKEN_HERE')",
            )

        sources = ConfigurationParser.get_value_if_key_exists(data, "channel.sources")
        if not isinstance(sources, list) or not sources:
            raise ValueError("channel.sources must be a non-empty list of channel IDs")

        try:
            raw_sources = [int(c) for c in sources]
        except (ValueError, TypeError) as err:
            raise ValueError(f"All items in channel.sources must be integer IDs: {err}") from err

        if any(c <= 0 for c in raw_sources):
            raise ValueError("All items in channel.sources must be positive integer channel IDs")

        channel_sources = tuple(dict.fromkeys(raw_sources))

        frequency = ConfigurationParser._parse_positive_int(data, "message.frequency")
        length_val = ConfigurationParser._parse_positive_int(data, "message.length")
        limit_val = ConfigurationParser._parse_positive_int(data, "message.limit")

        bot_app = ConfigurationParser._parse_id(data, "bot.app", "application ID")
        channel_target = ConfigurationParser._parse_id(data, "channel.target", "channel ID")

        return Configuration(
            bot_app=bot_app,
            bot_token=bot_token,
            channel_sources=channel_sources,
            channel_target=channel_target,
            message_farewell=str(
                ConfigurationParser.get_value_if_key_exists(data, "message.farewell"),
            ),
            message_frequency=frequency,
            message_length=length_val,
            message_limit=limit_val,
            message_warning=str(
                ConfigurationParser.get_value_if_key_exists(data, "message.warning"),
            ),
            message_welcome=str(
                ConfigurationParser.get_value_if_key_exists(data, "message.welcome"),
            ),
        )

    @staticmethod
    def to_dict(configuration: Configuration, *, mask_token: bool = True) -> dict[str, object]:
        return {
            "bot": {
                "app": configuration.bot_app,
                "token": "Secret token!" if mask_token else configuration.bot_token,
            },
            "channel": {
                "sources": list(configuration.channel_sources),
                "target": configuration.channel_target,
            },
            "message": {
                "farewell": configuration.message_farewell,
                "frequency": configuration.message_frequency,
                "length": configuration.message_length,
                "limit": configuration.message_limit,
                "warning": configuration.message_warning,
                "welcome": configuration.message_welcome,
            },
        }

    @staticmethod
    def get_json(configuration: Configuration) -> str:
        return json.dumps(ConfigurationParser.to_dict(configuration, mask_token=True), indent=2)

    @staticmethod
    def read_configuration(configuration_file_path: str) -> Configuration:
        return ConfigurationParser.verify_configuration_file(configuration_file_path)

    @staticmethod
    def write_configuration_to_file(path_to_write: str, configuration: Configuration) -> None:
        target_path = Path(path_to_write)
        with target_path.open("w", encoding="utf-8") as f:
            json.dump(ConfigurationParser.to_dict(configuration, mask_token=False), f, indent=2)
