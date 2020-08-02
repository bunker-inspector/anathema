from handler import Handler
import hashlib
import kv
import json
import random
import re

class CommandRegistry:
    def __init__(self, r):
        self.r = r
        stored_commands = r.get(kv.to_key(b'commands')) or '{}'
        self.registry = json.loads(stored_commands)

class RollHandler(Handler):
    roll_key = kv.to_key(b'roll')

    def __init__(self, r, commands={}):
        self.r = r
        self.registry = CommandRegistry(r)

    def accepts(self, message):
        return (message.content.startswith('!roll ')
        or message.content.startswith('!are-we-cursed?')
        or message.content == '!reset-curse')

    def _split_by_format(self, matches):
        rolls = []
        mods = []

        for match in matches:
            if re.match(r'\d+[d]\d+', match):
                rolls.append(match)
            elif re.match(r'\d+', match):
                mods.append(match)
            else:
                raise "FUCK FUCK FUCK"
        return [rolls, mods]

    def _roll(self, roll):
        times, die = map(int, roll.split('d'))

        return [random.randint(1, die) for _ in range(times)]

    def _get_roll_potential(self, rolls):
        roll_potential = 0

        for roll in rolls:
            times, die = map(int, roll.split('d'))
            roll_potential += die * times

        return roll_potential

    def _update_curse_data(self, total, potential):
       curse_data = self.r.get(self.roll_key)
       if not curse_data:
           curse_data = {'total': 0, 'potential': 0}
       else:
           curse_data = json.loads(curse_data)

       curse_data['total'] = curse_data['total'] + total
       curse_data['potential'] = curse_data['potential'] + potential

       self.r.set(self.roll_key, json.dumps(curse_data))

    def get_response(self, message):
        if message.content.startswith('!roll'):
            return self.get_roll_response(message)
        elif message.content.startswith('!are-we-cursed?'):
            return self.get_curse_query_response()
        elif message.content.strip() == '!reset-curse':
            return self.reset_response()
        return False

    def reset_response(self):
        self.r.delete(self.roll_key)

        return 'Curse data reset'

    def get_curse_query_response(self):
        curse_data = self.r.get(self.roll_key)

        if not curse_data:
            return 'There is not enough history to know if we are cursed.'

        curse_data = json.loads(curse_data)
        total = curse_data['total']
        potential = curse_data['potential']

        cursedness = total / potential

        if cursedness > .9:
            message = "The gods smile up on you."
        elif cursedness > .75:
            message = "You are blessed."
        elif cursedness > .6:
            message = "You have nothing to complain about."
        elif cursedness > .4:
            message = "Your dice work as intended."
        elif cursedness > .25:
            message = "You are fairly cursed."
        else:
            message = "Y'all are absolutely fucked"

        return "Cursedness: `{} / {} = {}` : {}".format(total, potential, cursedness, message)

    def get_roll_response(self, message):
        # Remove !roll from content
        reason = None
        split_command = [x.strip() for x in message.content[5:].split('!')]

        roll_clause = split_command[0]
        if len(split_command) > 1:
            reason = split_command[1]

        if not re.match(r'^(\d+[d]\d+|\-?\d+)(\+?(\d+[d]\d+|\-?\d+))*', roll_clause):
            return 'What the _fuck_ was that? Read the goddamned docs.'

        matches = re.findall(r'\+?(\d+[d]\d+|\-?\d+)', message.content)
        rolls, mods = self._split_by_format(matches)
        roll_results = [self._roll(roll) for roll in rolls]

        results_str = ','.join(map(str, roll_results))
        response = "{} rolled: `{}".format(message.author.name, results_str)

        if mods:
            response += " + {}".format(' + '.join(mods))
        response += '` '

        roll_total = sum(map(sum, roll_results))
        mod_total = sum(map(int, mods))

        roll_potential = self._get_roll_potential(rolls)
        total = roll_total + mod_total

        self._update_curse_data(total, roll_potential)

        response += 'for a total of `{}`'.format(total)

        if reason:
            response += ' to: {}'.format(reason)

        return response
