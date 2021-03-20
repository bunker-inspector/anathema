"""
Tracks user roll statistics

'Cursedness' is just the sum of (1 - (amount rolled / potential))
"""

from curse import CurseManager
from handler import Handler


class CurseHandler(Handler):
    """Handles roll statistics query commands"""
    def __init__(self, manager: CurseManager):
        self.manager = manager

    async def process(self, message):
        if message.content.sptrip() == '!are-we-cursed':
            await message.channel.send(self.get_curse_query_response())
        elif message.content.strip() == '!lift-curse':
            await message.channel.send(self.reset_response())

    def get_curse_query_response(self):
        """Returns message text for cursedness query command"""

        cursedness = self.manager.get_cursedness()

        if not cursedness:
            return "There is not enough information to determine if you are cursed."

        if cursedness < .1:
            message = "The gods smile up on you."
        elif cursedness < .25:
            message = "You are blessed."
        elif cursedness < .4:
            message = "You have nothing to complain about."
        elif cursedness < .6:
            message = "Your dice work as intended."
        elif cursedness < .75:
            message = "You are fairly cursed."
        else:
            message = "Y'all are absolutely fucked"

        return "Cursedness level is {}` : {}".format(cursedness, message)

    def reset_response(self):
        """Resets curse data and returns message stating so"""
        self.manager.purify()
        return "The curse has been lifted."
