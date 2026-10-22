from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_LOGGING_LEVEL = 20

LOGGING_LEVEL_CHOICES: dict[str, int] = {
    "CRITICAL": 50,
    "FATAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "WARN": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0,
}


@dataclass(slots=True, frozen=True)
class Arguments:
    configuration_path: str
    logging_level: int


def _parse_logging_level(val: str) -> int:
    val_upper = val.strip().upper()
    if val_upper in LOGGING_LEVEL_CHOICES:
        return LOGGING_LEVEL_CHOICES[val_upper]
    if val.isdigit() and int(val) in {0, 10, 20, 30, 40, 50}:
        return int(val)
    msg = (
        f"Invalid logging level: '{val}'. Choose from DEBUG, INFO, WARNING, ERROR, CRITICAL "
        "or 0, 10, 20, 30, 40, 50."
    )
    raise argparse.ArgumentTypeError(msg)


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
            type=_parse_logging_level,
            default=DEFAULT_LOGGING_LEVEL,
            help="Sets the logging level (e.g. DEBUG, INFO, WARNING, ERROR or 10, 20, 30).",
        )
        return parser

    @classmethod
    def parse_arguments(cls, args: Sequence[str] | None = None) -> Arguments:
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

        return Arguments(
            configuration_path=parsed.configuration_path,
            logging_level=parsed.logging_level,
        )

    @classmethod
    def verify_arguments(cls, args: Sequence[str] | None = None) -> Arguments:
        parsed = cls.parse_arguments(args)
        cls.configuration_path = parsed.configuration_path
        cls.logging_level = parsed.logging_level
        return parsed
