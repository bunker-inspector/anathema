class Handler:
    def __init__(self):
        pass

    def accepts(message):
        return False

    def get_response(message):
        return ''

    async def process(self, message):
        if self.accepts(message):
            await message.channel.send(self.get_response(message))
