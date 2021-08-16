from discord import Client
from discord.ext import tasks
import asyncio
import random

class Dumas(Client):

  def __init__(self, config):
    super(Dumas, self).__init__()
    self.messages = []
    self.config = config

  async def send_message_in_loop(self):
    while True:
      index = random.randint(0, len(self.messages) - 1)
      await self.target_channel.send(self.messages[index])
      await asyncio.sleep(self.config.message_frequency)

  async def on_ready(self):
    self.target_channel = self.get_channel(self.config.target_channel)
    for channel_id in self.config.source_channels:
      channel = self.get_channel(channel_id)
      async for msg in channel.history(limit=self.config.message_limit):
        if msg.content != '' and msg.author.id != self.config.bot_id and len(msg.content) >= self.config.min_message_length and not msg.content.startswith('-p') and not msg.content.startswith('-skip'):
          self.messages.append(msg.content)
    await self.target_channel.send(self.config.first_message)
    self.loop.create_task(self.send_message_in_loop())
