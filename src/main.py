from configreader import ConfigReader
from dumas import Dumas
from os import path
import time
import sys

if __name__ == '__main__':
  config_path = sys.argv[1]
  while not path.exists(config_path):
    time.sleep(60)
  configReader = ConfigReader(config_path)
  configReader.read()
  config = configReader.get_config()
  Dumas(config).run(config.token)
