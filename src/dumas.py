from discord import Client
from discord.ext import tasks

from configutil import ConfigUtil
from message import Message
from timeutil import TimeUtil

import asyncio, logging, random, time

logger = logging.getLogger(__name__)

HELP='''```
Usage:
  &help       - show this help page
  &start      - start sending messages continously
  &stop       - stop sending messages continously
  &random     - send a random message once
  &get-config - get active configuration
```'''

class Dumas(Client):

  def __init__(self, config):
    super(Dumas, self).__init__()
    self.active = False
    self.config = config
    self.authors = []
    self.messages = []

  async def on_ready(self):
    logger.info('Bot is ready!')
    self.target_channel = self.get_channel(self.config.channel_target)
    await self.read_history()
    await self.target_channel.send(self.config.message_welcome)

  async def on_message(self, message):
    logger.info('Got a message!')
    author_id = await self.get_author_id_from_message_content_if_present(message.content)
    print(author_id)
    print(self.config.bot_app)
    if author_id == str(self.config.bot_app):
      await self.target_channel.send(self.config.message_warning)
    if message.content.startswith('&help'):
      await self.show_help()
    elif message.content.startswith('&start'):
      self.active = True
      await self.send_messages_continously(author_id)
    elif message.content.startswith('&stop'):
      await self.stop_sending_messages()
    elif message.content.startswith('&random'):
      await self.send_random_message(author_id)
    elif message.content.startswith('&get-config'):
      await self.get_config()

  async def show_help(self):
    logger.info('Showing help!')
    await self.target_channel.send(HELP)

  async def send_messages_continously(self, author_id = None):
    logger.info('Starting to send messages...')
    while self.active:
      await self.send_random_message(author_id)
      await asyncio.sleep(self.config.message_frequency)

  async def stop_sending_messages(self):
    logger.info('Stopping messages!')
    self.active = False

  async def send_random_message(self, author_id = None):
    logger.info('Sending a random message...')
    index = random.randint(0, len(self.messages) - 1)
    if author_id != None:
      while self.messages[index].author_id != author_id:
        index = random.randint(0, len(self.messages) - 1)
    await self.target_channel.send(self.messages[index].content)

  async def get_config(self):
    logger.info('Showing config!')
    await self.target_channel.send('```json' + ConfigUtil.get_config_json(self.config) + '```')

  async def read_history(self):
    logger.info('Starting to read history...')
    start_epochs = time.time()
    for channel_id in self.config.channel_sources:
      channel = self.get_channel(channel_id)
      async for msg in channel.history(limit=self.config.message_limit):
        message = Message(author_id = msg.author.id, content = msg.content)
        if message.is_relevant(self.config):
          self.messages.append(message)
          if message.author_id not in self.authors:
            self.authors.append(message.author_id)
    end_epochs = time.time()
    logger.info('History reading have lasted for ' + str(TimeUtil.get_time_between_epochs(start_epochs, end_epochs)) + ' seconds.')

  async def get_author_id_from_message_content_if_present(self, message_content):
    splitted_message = message_content.split(' ')
    if len(splitted_message) == 2:
      author_id = splitted_message[1]
      if author_id in self.authors or author_id == str(self.config.bot_app):
        return author_id
