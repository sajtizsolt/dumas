from discord import Client
from discord.ext import tasks

from configurationparser import ConfigurationParser
from message import Message

import asyncio, logging, random, time

logger = logging.getLogger(__name__)

HELP='''```
Usage:
  &help               - show this help page
  &start [author_id]  - start sending messages continously (from the specified user)
  &stop               - stop sending messages continously
  &random [author_id] - send a random message once (from the specified user)
  &show-config        - show active configuration
```'''

class Dumas(Client):

  def __init__(self, configuration):
    super(Dumas, self).__init__()
    self.authors = []
    self.configuration = configuration
    self.messages = {}
    self.sending_messages = False
    self.target_channel = None

  async def on_ready(self):
    logger.info('Dumas is ready.')
    await self.read_message_history()
    self.target_channel = self.get_channel(self.configuration.channel_target)
    await self.send_message(self.configuration.message_welcome)

  async def read_message_history(self):
    start = time.time()
    logger.info('Starting to read message history...')
    for channel_id in self.configuration.channel_sources:
      channel = self.get_channel(channel_id)
      async for msg in channel.history(limit=self.configuration.message_limit):
        message = Message(author_id = msg.author.id, content = msg.content)
        if message.is_relevant(self.configuration):
          if message.author_id not in self.authors:
            self.authors.append(message.author_id)
            self.messages[message.author_id] = []
          self.messages[message.author_id].append(message)
    logger.info('Finished reading message history!')
    logger.info('Elapsed time: {} seconds'.format(time.time() - start))

  async def send_message(self, message):
    ZERO_WIDTH_PREFIX = '\u200B\u200D\uFEFF'
    await self.target_channel.send(ZERO_WIDTH_PREFIX + str(message))

  async def on_message(self, message):
    logger.info('Someone sent a message.')
    author_id = await self.get_author_id_from_message(message)
    if author_id == self.configuration.bot_app:
      await self.send_message(self.configuration.message_warning)
    elif message.content.startswith('&help'):
      await self.show_help()
    elif message.content.startswith('&start'):
      await self.send_messages_continously(author_id)
    elif message.content.startswith('&stop'):
      await self.stop_sending_messages_continously()
    elif message.content.startswith('&random'):
      await self.send_random_message(author_id)
    elif message.content.startswith('&show-config'):
      await self.show_configuration()

  async def get_author_id_from_message(self, message):
    if message.content.startswith('&'):
      splitted_message = message.content.split(' ')
      if len(splitted_message) == 2:
        author_id = int(splitted_message[1])
        return author_id

  async def show_help(self):
    logger.info('Showing help.')
    await self.send_message(HELP)

  async def send_messages_continously(self, author_id):
    logger.info('Starting to send messages continously.')
    self.sending_messages = True
    while self.sending_messages:
      await self.send_random_message(author_id)
      await asyncio.sleep(self.configuration.message_frequency)

  async def stop_sending_messages_continously(self):
    logger.info('Stopping to send messages continously.')
    self.sending_messages = False

  async def send_random_message(self, author_id):
    logger.info('Sending a random message.')
    author_index = random.randint(0, len(self.authors) - 1)
    if author_id != None:
      author_index = self.authors.index(author_id)
    message_index = random.randint(0, len(self.messages[self.authors[author_index]]) - 1)
    await self.send_message(self.messages[self.authors[author_index]][message_index].content)

  async def show_configuration(self):
    logger.info('Showing configuration.')
    await self.send_message('```json' + ConfigurationParser.get_json(self.configuration) + '```')
