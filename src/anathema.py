"""
Entrypoint
"""

import os
import discord
from rocksdb import DB, Options
from characterhandler import CharacterHandler
from commandhandler import CommandHandler
from inspirehandler import InspireHandler
from kv import KV
from rollhandler import RollHandler

if __name__ == '__main__':
    client = discord.Client()

    rocks_db_location = os.getenv('ROCKS_DB_LOCATION', 'anathema.db')
    kv = KV(DB(rocks_db_location, Options(create_if_missing=True)))

    handlers = [RollHandler(kv), InspireHandler(), CharacterHandler(kv)]

    command_handler = CommandHandler(kv, handlers.copy())

    handlers.append(command_handler)

    @client.event
    async def on_ready():
        """Handles bot start"""
        print('We have logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        """Entry point for all message handling"""
        if message.author == client.user:
            return

        for handler in handlers:
            await handler.process(message)

    client.run(os.getenv('DISCORD_BOT_TOKEN'))
