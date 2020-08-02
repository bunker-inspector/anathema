import discord
import os
import redis
from roll import RollHandler
from command import CommandHandler

if __name__ == '__main__':
    client = discord.Client()

    redis_host = os.getenv('REDIS_HOST') or 'localhost'
    redis_port = os.getenv('REDIS_PORT') or 6379
    redis_db   = os.getenv('REDIS_DB') or 0
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

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
