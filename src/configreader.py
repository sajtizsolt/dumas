from dataclasses import dataclass
import json

@dataclass
class Config:
  bot_id: int
  token: int
  source_channels: list[int]
  target_channel: int
  message_limit: int
  message_frequency: int
  min_message_length: int
  first_message: str

class ConfigReader:

  def __init__(self, filepath):
    self.filepath = filepath

  def read(self):
    configFile = open(self.filepath)
    data = json.load(configFile)
    configFile.close()
    self.config = Config(data['botId'], data['token'], data['sourceChannels'], data['targetChannel'], data['messageLimit'], data['messageFrequency'], data['minimumMessageLength'], data['firstMessage'])

  def get_config(self):
    return self.config
