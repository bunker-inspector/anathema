"""
Provides motivation
"""

import json
import random
from handler import Handler


class InspireHandler(Handler):
    """Handles inspiration"""
    def __init__(self):
        self.aow = json.loads(open('aow.json', 'r').read())

    def accepts(self, message):
        return message.content.strip() == '!inspire'

    async def process(self, message):
        if not self.accepts(message):
            return

        chapter_ct = len(self.aow['chapters'])

        chapter = self.aow['chapters'][random.randint(0, chapter_ct - 1)]

        chapter_contents = self.aow['contents'][chapter]

        contents_ct = len(chapter_contents)

        content = self.aow['contents'][chapter][random.randint(
            0, contents_ct - 1)]

        content = content[content.find('.') + 2:]

        await message.channel.send('Sun Tzu says: \n > {}'.format(content))
