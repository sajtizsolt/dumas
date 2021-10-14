from argumentparser import ArgumentParser
from configuration import Configuration
from util import print_exception_and_exit, print_message_and_exit

import json, os

CONFIGURATION_JSON = """
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
    "warning": "{}",
    "welcome": "{}"
  }}
}}"""

class ConfigurationParser:

  MISSING_KEY_MESSAGE = """
    Configuration file does not contain the following key: {}
  """

  @staticmethod
  def get_value_if_key_exists(dictionary, key_with_dots):
    try:
      keys = key_with_dots.split('.')
      for key in keys:
        if key in dictionary:
          dictionary = dictionary[key]
        else:
          raise KeyError()
      return dictionary
    except KeyError:
      print_message_and_exit(ConfigurationParser.MISSING_KEY_MESSAGE.format(key_with_dots))

  @staticmethod
  def verify_configuration_file(configuration_file_path):
    try:
      if not os.path.isfile(configuration_file_path):
        raise ValueError(ArgumentParser.INVALID_CONFIGURATION_FILE_PATH)
      configuration_file = open(configuration_file_path, encoding="utf-8")
      data = json.load(configuration_file)
      configuration_file.close()
      return Configuration(
        bot_app = ConfigurationParser.get_value_if_key_exists(data, 'bot.app'),
        bot_token = ConfigurationParser.get_value_if_key_exists(data, 'bot.token'),
        channel_sources = ConfigurationParser.get_value_if_key_exists(data, 'channel.sources'),
        channel_target = ConfigurationParser.get_value_if_key_exists(data, 'channel.target'),
        message_farewell = ConfigurationParser.get_value_if_key_exists(data, 'message.farewell'),
        message_frequency = ConfigurationParser.get_value_if_key_exists(data, 'message.frequency'),
        message_length = ConfigurationParser.get_value_if_key_exists(data, 'message.length'),
        message_limit = ConfigurationParser.get_value_if_key_exists(data, 'message.limit'),
        message_warning = ConfigurationParser.get_value_if_key_exists(data, 'message.warning'),
        message_welcome = ConfigurationParser.get_value_if_key_exists(data, 'message.welcome'),
      )
    except ValueError:
      print_exception_and_exit()

  @staticmethod
  def get_json(configuration):
    return CONFIGURATION_JSON.format(
      configuration.bot_app,
      "Secret token!",
      configuration.channel_sources,
      configuration.channel_target,
      configuration.message_farewell,
      configuration.message_frequency,
      configuration.message_length,
      configuration.message_limit,
      configuration.message_warning,
      configuration.message_welcome
    )

  @staticmethod
  def read_configuration(configuration_file_path):
    configuration_file = open(configuration_file_path, encoding="utf-8")
    data = json.load(configuration_file)
    configuration_file.close()
    return Configuration(
      bot_app = data['bot']['app'],
      bot_token = data['bot']['token'],
      channel_sources = data['channel']['sources'],
      channel_target = data['channel']['target'],
      message_farewell = data['message']['farewell'],
      message_frequency = data['message']['frequency'],
      message_length = data['message']['length'],
      message_limit = data['message']['limit'],
      message_warning = data['message']['warning'],
      message_welcome = data['message']['welcome']
    )

  @staticmethod
  def write_configuration_to_file(path_to_write, configuration):
    configuration_file = open(path_to_write, 'w', encoding="utf-8")
    configuration_file.write(ConfigurationParser.get_json(configuration))
    configuration_file.close()
