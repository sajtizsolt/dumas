from config import Config

import json

class ConfigUtil:

  @staticmethod
  def read_config(path):
    config_file = open(path)
    data = json.load(config_file)
    config_file.close()
    return Config(
      bot_app = data['bot']['app'],
      bot_token = data['bot']['token'],
      channel_sources = data['channel']['sources'],
      channel_target = data['channel']['target'],
      message_farewell = data['message']['farewell'],
      message_frequency = data['message']['frequency'],
      message_length = data['message']['length'],
      message_limit = data['message']['limit'],
      message_welcome = data['message']['welcome']
    )
