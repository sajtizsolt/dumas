import json
import logging
import sys

from dotenv import load_dotenv

from .argumentparser import ArgumentParser
from .configurationparser import ConfigurationParser
from .dumas import Dumas

logger = logging.getLogger(__name__)


def configure_logger(logging_level: int = 20) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler("dumas.log", encoding="utf-8"))
    except OSError as err:
        logger.warning("Could not open 'dumas.log' for writing: %s. Logging to console only.", err)

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )


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
    try:
        bot.run(configuration.bot_token, log_handler=None)
    except KeyboardInterrupt:
        logger.info("Bot process interrupted by user. Exiting.")


if __name__ == "__main__":
    main()
