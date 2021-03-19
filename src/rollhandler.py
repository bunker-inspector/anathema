"""
Slathers the button on the bread
"""

from handler import Handler
from roll import Roll


class RollHandler(Handler):
    """Returns like 99% of responses I promise"""
    def __init__(self, kv):
        self.kv = kv

    def accepts(self, message):
        return (message.content.lower().startswith('!roll ')
                or message.content.startswith('!are-we-cursed?')
                or message.content == '!reset-curse')

    async def process(self, message):
        if not self.accepts(message):
            return
        if message.content.lower().startswith('!roll'):
            await message.channel.send(self.get_roll_response(message))

    def get_roll_response(self, message):
        """Creates rolls response text"""
        # Remove !roll from content
        reason = None
        split_command = [x.strip() for x in message.content[5:].split('!', 1)]

        if len(split_command) > 1:
            reason = split_command[1]

        roll = Roll.from_expr(split_command[0])
        if not roll:
            return "Did not conform to spec: Check the docs, which there are none of."
        results, total = roll.get()

        msg = "{} rolled `{}` for a total of `{}`".format(
            message.author.nick, ' + '.join(map(str, results)), total)
        if reason:
            msg += ": {}".format(reason)

        return msg
