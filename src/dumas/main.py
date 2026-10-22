import json
import logging
import sys

from dotenv import load_dotenv

from .argumentparser import ArgumentParser
from .configurationparser import ConfigurationParser
from .dumas import Dumas

logger = logging.getLogger(__name__)


def configure_logger(logging_level: int = 20) -> None:
    logging.basicConfig(
        encoding="utf-8",
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        filename="dumas.log",
        level=logging_level,
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging_level)
    logging.getLogger().addHandler(console_handler)


def main() -> None:
    load_dotenv()
    parsed_args = ArgumentParser.verify_arguments()
    configure_logger(parsed_args.logging_level)

    try:
        configuration = ConfigurationParser.verify_configuration_file(
            parsed_args.configuration_path,
        )
    except FileNotFoundError, KeyError, json.JSONDecodeError, TypeError, ValueError:
        logger.exception("Failed to load configuration")
        sys.exit(1)

    bot = Dumas(configuration)
    bot.run(configuration.bot_token)


if __name__ == "__main__":
    main()
