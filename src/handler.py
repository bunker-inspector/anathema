"""
Provides interface for all message handlers
"""


class Handler:
    """Handler interface"""
    def accepts(self, _message):
        """Returns boolean stating whether handler impl will respond to a given message"""

    def get_response(self, _message):
        """Reurns response to message"""

    async def process(self, message):
        """Processes message"""
        if self.accepts(message):
            await message.channel.send(self.get_response(message))
