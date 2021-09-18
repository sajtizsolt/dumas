from dumas import Dumas
from configutil import ConfigUtil

import logging, os, sys, time

def show_help():
  print('Usage:')
  print('  python main.py <absolute-config-file-path>')

def check_arguments(arguments):
  if len(arguments) != 2:
    show_help()
    logging.error('Invalid command line arguments!')
    os._exit(1)

def wait_for_config_file(path):
  while not os.path.exists(path):
    logging.info('Waiting for configuration file to appear...')
    time.sleep(60)

if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s %(message)s', filename='dumas.log', encoding='utf-8', level=logging.INFO)
  logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
  logging.info('Logging to dumas.log in UTF-8 encoding and INFO level.')
  check_arguments(sys.argv)
  wait_for_config_file(sys.argv[1])
  config = ConfigUtil.read_config(sys.argv[1])
  logging.debug('Configuration file content:')
  logging.debug(ConfigUtil.get_config_json(config))
  Dumas(config).run(config.bot_token)
