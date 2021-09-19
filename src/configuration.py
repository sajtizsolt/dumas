from dataclasses import dataclass

@dataclass
class Configuration:

  bot_app: int
  bot_token: str
  channel_sources: list[int]
  channel_target: int
  message_farewell: str
  message_frequency: int
  message_length: int
  message_limit: int
  message_warning: str
  message_welcome: str
