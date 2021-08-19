from config import Config

import json

CONFIG_JSON = """
{{
  "bot": {{
    "app": {},
    "token": "{}"
  }},
  "channel": {{
    "sources": {},
    "target": {}
  }},
  "message": {{
    "farewell": "{}",
    "frequency": {},
    "length": {},
    "limit": {},
    "welcome": "{}"
  }}
}}"""

class ConfigUtil:

  @staticmethod
  def get_config_json(config):
    return CONFIG_JSON.format(
      config.bot_app,
      "Secret token!",
      config.channel_sources,
      config.channel_target,
      config.message_farewell,
      config.message_frequency,
      config.message_length,
      config.message_limit,
      config.message_welcome
    )

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

  @staticmethod
  def write_config(path, config):
    config_file = open(path, 'w')
    config_file.write(ConfigUtil.get_config_json(config))
    config_file.close()
