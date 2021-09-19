from argumentparser import ArgumentParser
from configurationparser import ConfigurationParser
from dumas import Dumas

import logging, sys

def configure_logger():
  logging.basicConfig(
    encoding='utf-8',
    format='%(asctime)s %(message)s',
    filename='dumas.log',
    level=ArgumentParser.logging_level
  )
  logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

if __name__ == '__main__':
  ArgumentParser.verify_arguments()
  configure_logger()
  configuration = ConfigurationParser.verify_configuration_file(ArgumentParser.configuration_path)
  Dumas(configuration).run(configuration.bot_token)
