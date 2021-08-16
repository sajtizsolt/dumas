from configreader import ConfigReader
from dumas import Dumas
import sys

if __name__ == '__main__':
  configReader = ConfigReader(sys.argv[1])
  configReader.read()
  config = configReader.get_config()
  Dumas(config).run(config.token)
