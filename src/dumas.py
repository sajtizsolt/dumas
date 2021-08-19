from discord import Client
from discord.ext import tasks

from message import Message

import asyncio
import random

HELP='''```
Usage:
  &help   - show this help page
  &start  - start sending messages continously
  &stop   - stop sending messages continously
  &random - send a random message once
```'''

class Dumas(Client):

  def __init__(self, config):
    super(Dumas, self).__init__()
    self.active = False
    self.config = config
    self.messages = []

  async def on_ready(self):
    self.target_channel = self.get_channel(self.config.channel_target)
    for channel_id in self.config.channel_sources:
      channel = self.get_channel(channel_id)
      async for msg in channel.history(limit=self.config.message_limit):
        message = Message(author_id = msg.author.id, content = msg.content)
        if message.is_relevant(self.config):
          self.messages.append(message)
    await self.target_channel.send(self.config.message_welcome)
    await self.keep_alive()

  async def keep_alive(self):
    while True:
      self.target_channel.history(limit=1)
      await asyncio.sleep(900)

  async def on_message(self, message):
    if message.content.startswith('&help'):
      await self.show_help()
    elif message.content.startswith('&start'):
      self.active = True
      await self.send_messages_continously()
    elif message.content.startswith('&stop'):
      await self.stop_sending_messages()
    elif message.content.startswith('&random'):
      await self.send_random_message()

  async def show_help(self):
    await self.target_channel.send(HELP)

  async def send_messages_continously(self):
    while self.active:
      await self.send_random_message()
      await asyncio.sleep(self.config.message_frequency)

  async def stop_sending_messages(self):
    self.active = False

  async def send_random_message(self):
    index = random.randint(0, len(self.messages) - 1)
    await self.target_channel.send(self.messages[index].content)
