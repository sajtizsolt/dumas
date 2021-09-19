from dataclasses import dataclass

GROOVY_COMMANDS = ['-p', '-skip', '-loop', '-q', '-clear', '-remove', '-dc']
DUMAS_COMMANDS = ['&help', '&start', '&stop', '&random', '&get-config', '&show-config']
ZERO_WIDTH_PREFIXES = ['\u200B', '\u200D', '\uFEFF']

@dataclass
class Message:

  author_id: int
  content: str

  def is_relevant(self, configuration):
    for prefix in ZERO_WIDTH_PREFIXES:
      if self.content.startswith(prefix):
        return False
    if self.author_id == configuration.bot_app:
      return False
    if len(self.content) < configuration.message_length:
      return False
    for cmd in GROOVY_COMMANDS:
      if self.content.startswith(cmd):
        return False
    for cmd in DUMAS_COMMANDS:
      if self.content.startswith(cmd):
        return False
    return True
