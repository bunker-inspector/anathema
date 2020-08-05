import discord
import os
import rocksdb
from roll import RollHandler
from command import CommandHandler

if __name__ == '__main__':
    client = discord.Client()

    rocks_db_location = os.getenv("ROCKS_DB_LOCATION", "anathema.db")
    r = rocksdb.DB(rocks_db_location, rocksdb.Options(create_if_missing=True))

    handlers = [RollHandler(r)]

    command_handler = CommandHandler(r, handlers)

    handlers.append(command_handler)

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        print(message)
        if message.author == client.user:
            return

        for handler in handlers:
            if handler.accepts(message):
                response = handler.get_response(message)
                if response: await message.channel.send(response)

    client.run(os.getenv('DISCORD_BOT_TOKEN'))
