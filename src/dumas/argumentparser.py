import argparse
import os
from pathlib import Path

DEFAULT_LOGGING_LEVEL = 20


class ArgumentParser:
    configuration_path: str = ""
    logging_level: int = DEFAULT_LOGGING_LEVEL

    @staticmethod
    def get_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="dumas",
            description="A Discord bot written in Python to bring back memories.",
        )
        parser.add_argument(
            "configuration_path",
            nargs="?",
            default=os.getenv("DUMAS_CONFIG", ""),
            help="Path to the JSON configuration file (or set via DUMAS_CONFIG env var).",
        )
        parser.add_argument(
            "--logging-level",
            type=int,
            choices=[0, 10, 20, 30, 40, 50],
            default=DEFAULT_LOGGING_LEVEL,
            help="Sets the logging level of the application (0, 10, 20, 30, 40, or 50).",
        )
        return parser

    @classmethod
    def parse_arguments(cls, args: list[str] | None = None) -> argparse.Namespace:
        parser = cls.get_parser()
        parsed = parser.parse_args(args)

        if not parsed.configuration_path:
            parser.error(
                "You must specify at least the configuration file path of the application "
                "or set the DUMAS_CONFIG environment variable.",
            )

        config_path = Path(parsed.configuration_path)
        if not config_path.is_file():
            parser.error(
                f"The specified configuration file path is invalid: '{parsed.configuration_path}'. "
                "Please check if the given file exists.",
            )

        return parsed

    @classmethod
    def verify_arguments(cls, args: list[str] | None = None) -> argparse.Namespace:
        parsed = cls.parse_arguments(args)
        cls.configuration_path = parsed.configuration_path
        cls.logging_level = parsed.logging_level
        return parsed
