from dataclasses import dataclass

@dataclass
class Message:

  author_id: int
  content: str

  def is_relevant(self, config):
    if self.author_id == config.bot_app:
      return False
    if len(self.content) < config.message_length:
      return False
    for cmd in ['-p', '-skip', '-loop', '-q', '-clear', '-remove', '-dc']:
      if self.content.startswith(cmd):
        return False
    for cmd in ['&help', '&start', '&stop', '&random', '&get-config']:
      if self.content.startswith(cmd):
        return False
    return True
