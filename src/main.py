from configreader import ConfigReader
from dumas import Dumas

import os, sys, time

def show_help():
  print('Usage:')
  print('  python main.py <absolute-config-file-path>')

def check_arguments(arguments):
  if len(arguments) != 2:
    show_help()
    os._exit(1)

def wait_for_config_file(path):
  while not os.path.exists(path):
    time.sleep(60)

def get_config(path):
  configReader = ConfigReader(path)
  configReader.read()
  return configReader.get_config()

if __name__ == '__main__':
  check_arguments(sys.argv)
  wait_for_config_file(sys.argv[1])
  config = get_config(sys.argv[1])
  Dumas(config).run(config.bot_token)
