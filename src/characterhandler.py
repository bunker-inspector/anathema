from handler import Handler
import json

PROFICIENCIES = {
    'perception': 'wis',
    'fortitude': 'con',
    'reflex': 'dex',
    'will': 'wis',
    'acrobatics': 'dex',
    'arcana': 'int',
    'athletics': 'str',
    'crafting': 'int',
    'deception': 'cha',
    'diplomacy': 'cha',
    'intimidation': 'cha',
    'medicine': 'wis',
    'nature': 'wis',
    'occultism': 'int',
    'performance': 'cha',
    'religion': 'wis',
    'society': 'int',
    'stealth': 'dex',
    'survival': 'wis',
    'thievery': 'dex'
}


class CharacterHandler(Handler):
    def __init__(self, kv):
        self.kv = kv

    async def process(self, message):
        if self.is_character_set(message):
            await self._process_character_set(message)
        elif self.is_character_me(message):
            await self._process_character_me(message)

    def _char_key(self, message):
        return 'character-{}'.format(message.author.id)

    def is_character_set(self, message):
        if message.content.strip() != '!char set':
            return False
        if len(message.attachments) != 1:
            return False
        if not message.attachments[0].filename.endswith('.json'):
            return False
        return True

    def is_character_me(self, message):
        return message.content.strip() == '!char me'

    async def _process_character_me(self, message):
        c = self.kv.get(self._char_key(message))
        res = "{}: Level {} {} {}".format(c['name'], c['level'], c['ancestry'],
                                          c['class'])
        await message.channel.send(res)

    async def _process_character_set(self, message):
        character_data = json.loads(
            (await message.attachments[0].read()).decode('utf-8'))['build']
        self.kv.put(self._char_key(message), character_data)

        await message.channel.send('"{}" has been uploaded.'.format(
            character_data['name']))
