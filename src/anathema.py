import discord
import os
from rollhandler import RollHandler
from characterhandler import CharacterHandler
from commandhandler import CommandHandler
from inspirehandler import InspireHandler
from kv import KV
from rocksdb import DB, Options

if __name__ == '__main__':
    client = discord.Client()

    rocks_db_location = os.getenv('ROCKS_DB_LOCATION', 'anathema.db')
    kv = KV(DB(rocks_db_location, Options(create_if_missing=True)))

    handlers = [RollHandler(kv), InspireHandler(), CharacterHandler(kv)]

    command_handler = CommandHandler(kv, handlers.copy())

    handlers.append(command_handler)

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        for handler in handlers:
            await handler.process(message)

    client.run(os.getenv('DISCORD_BOT_TOKEN'))
