from dumas import Dumas
from configutil import ConfigUtil

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

if __name__ == '__main__':
  check_arguments(sys.argv)
  wait_for_config_file(sys.argv[1])
  config = ConfigUtil.read_config(sys.argv[1])
  Dumas(config).run(config.bot_token)
