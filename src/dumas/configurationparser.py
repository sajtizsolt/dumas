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
    def verify_configuration_file(configuration_file_path: str) -> Configuration:
        config_path = Path(configuration_file_path)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {configuration_file_path}")

        with config_path.open(encoding="utf-8") as f:
            data: dict[str, object] = json.load(f)

        raw_token = str(ConfigurationParser.get_value_if_key_exists(data, "bot.token"))
        env_token = os.getenv("DISCORD_TOKEN")
        if env_token and (not raw_token or raw_token in ("ENV", "YOUR_TOKEN_HERE")):
            bot_token = env_token
        else:
            bot_token = raw_token

        sources = ConfigurationParser.get_value_if_key_exists(data, "channel.sources")
        if not isinstance(sources, list):
            raise TypeError("channel.sources must be a list of channel IDs")

        target_id = ConfigurationParser.get_value_if_key_exists(data, "channel.target")
        limit_val = ConfigurationParser.get_value_if_key_exists(data, "message.limit")

        return Configuration(
            bot_app=int(str(ConfigurationParser.get_value_if_key_exists(data, "bot.app"))),
            bot_token=bot_token,
            channel_sources=[int(c) for c in sources],
            channel_target=int(str(target_id)),
            message_farewell=str(
                ConfigurationParser.get_value_if_key_exists(data, "message.farewell"),
            ),
            message_frequency=int(
                str(ConfigurationParser.get_value_if_key_exists(data, "message.frequency")),
            ),
            message_length=int(
                str(ConfigurationParser.get_value_if_key_exists(data, "message.length")),
            ),
            message_limit=int(str(limit_val)),
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
                "sources": configuration.channel_sources,
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
