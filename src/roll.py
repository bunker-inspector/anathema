from handler import Handler
import hashlib
import kv
import json
import random
import re

class RollHandler(Handler):
    roll_key = kv.to_key(b'roll')

    def __init__(self, r, commands={}):
        self.r = r

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

    def _update_curse_data(self, cursedness, num_rolls):
       curse_data = self.r.get(self.roll_key)
       if not curse_data:
           curse_data = {'total_curse': 0.0, 'total_rolls': 0}
       else:
           curse_data = json.loads(curse_data.decode('UTF-8'))

       curse_data['total_curse'] = curse_data['total_curse'] + cursedness
       curse_data['total_rolls'] = curse_data['total_rolls'] + num_rolls

       self.r.put(self.roll_key, json.dumps(curse_data).encode('UTF-8'))

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

        curse_data = curse_data.decode('UTF-8')

        curse_data = json.loads(curse_data)
        total_curse = curse_data['total_curse']
        total_rolls = curse_data['total_rolls']

        cursedness = total_curse / total_rolls

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

        return "Cursedness: `{} / {} = {}` : {}".format(total_curse, total_rolls, cursedness, message)

    def _get_cursedness(self, rolls, roll_results):
        total_cursedness = 0.0
        for idx, roll in enumerate(rolls):
            roll_potential = int(roll.split('d')[1])
            results_in_set = roll_results[idx]
            for result in results_in_set:
                print("Rolled {} / {} : Blessdness {}".format(result, roll_potential, result / roll_potential))
                total_cursedness += (result-1) / (roll_potential-1)
        return total_cursedness

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

        total = roll_total + mod_total

        cursedness = self._get_cursedness(rolls, roll_results)
        self._update_curse_data(cursedness, sum(map(len, roll_results)))

        response += 'for a total of `{}`'.format(total)

        if reason:
            response += ' to: {}'.format(reason)

        return response
