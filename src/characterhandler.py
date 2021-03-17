from handler import Handler
from roll import Roll, DiceRoll, Modifier
import json

SKILLS = {
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
        elif self.is_roll_character(message):
            await self._process_roll_character(message)

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

    def is_roll_character(self, message):
        return message.content.strip().startswith('!rollc ')

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

    async def _process_roll_character(self, message):
        c = self.kv.get(self._char_key(message))
        if not c:
            await message.channel.send('You have not uploaded your character.')
            return

        tokens = message.content.strip().lower().split()[1:]
        skill = tokens[0]
        modifying_ability = SKILLS.get(skill, None)
        if not modifying_ability:
            await message.channel.send('{} is not supported.'.format(skill))
            return
        ability = c['abilities'][modifying_ability]
        ability_modifier = (ability - 10) // 2
        proficiency = c['proficiencies'][skill]
        level = c['level']

        base_modifier = ability_modifier + proficiency + level

        extra_mods = [Modifier(m) for m in map(int, tokens[1:])]

        rolls = [DiceRoll(1, 20), Modifier(base_modifier)]
        rolls.extend(extra_mods)

        r = Roll(rolls)
        results, total = r.get()

        msg = "{} rolled `{}` for a total of `{}`".format(
            message.author.nick, ' + '.join(map(str, results)), total)
        msg += ": {}".format(skill)

        await message.channel.send(msg)
