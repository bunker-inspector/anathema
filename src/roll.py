from handler import Handler
import hashlib
import kv
import json
import os
import random
import re

POS_EXPR = r'\s?[\+|\-]?\s?'
DIE_EXPR = r'{}\d+[d]\d+'.format(POS_EXPR)
MOD_EXPR = r'{}\d+'.format(POS_EXPR)
ROLL_EXPR = r'({}|{})'.format(DIE_EXPR, MOD_EXPR)
ROLLS_EXPR = r'{}*'.format(ROLL_EXPR)

KH_EXPR = r'kh\d+'
KL_EXPR = r'kl\d+'

XFORM_EXPRS = [KH_EXPR, KL_EXPR]

XFORM_EXPR = r'({})'.format('|'.join(XFORM_EXPRS))
COMMAND_EXPR = r'{}(\s+({}*))?'.format(ROLLS_EXPR, XFORM_EXPR)


class RollHandler(Handler):
    roll_key = kv.to_key(b'roll')

    def __init__(self, r, commands={}):
        self.r = r

    def accepts(self, message):
        return (message.content.lower().startswith('!roll ')
                or message.content.startswith('!are-we-cursed?')
                or message.content == '!reset-curse')

    def _split_by_format(self, matches):
        rolls = []
        mods = []

        for match in matches:
            match = match.replace(' ', '')
            if re.match(DIE_EXPR, match):
                rolls.append(match)
            elif re.match(MOD_EXPR, match):
                mods.append(match)
            else:
                raise "Wrong!"

        return [rolls, mods]

    ## Internal Helpers

    def _roll(self, roll):
        times, die = map(int, roll.split('d'))

        return [random.randint(1, die) for _ in range(times)]

    def _update_curse_data(self, rolls, roll_results):
        num_rolls = sum(map(len, roll_results))
        cursedness = self._get_cursedness(rolls, roll_results)

        curse_data = self.r.get(self.roll_key)

        if not curse_data:
            curse_data = {'total_curse': 0.0, 'total_rolls': 0}
        else:
            curse_data = json.loads(curse_data.decode('UTF-8'))

        curse_data['total_curse'] = curse_data['total_curse'] + cursedness
        curse_data['total_rolls'] = curse_data['total_rolls'] + num_rolls

        self.r.put(self.roll_key, json.dumps(curse_data).encode('UTF-8'))

    def _get_cursedness(self, rolls, roll_results):
        total_cursedness = 0.0
        for idx, roll in enumerate(rolls):
            roll_potential = int(roll.split('d')[1])
            results_in_set = roll_results[idx]
            for result in results_in_set:
                blessedness = 0.5 if roll_potential == 1 else (result - 1) / (
                    roll_potential - 1)
                print("Rolled {} / {} : Blessedness {}".format(
                    result, roll_potential, blessedness))
                total_cursedness += blessedness
        return total_cursedness

    def _apply_xforms(self, roll_results, xform_tokens):
        for token in xform_tokens:
            if re.fullmatch(KH_EXPR, token):
                take = int(token[2:])
                roll_results = map(lambda x: sorted(x)[-take:], roll_results)
            elif re.fullmatch(KL_EXPR, token):
                take = int(token[2:])
                roll_results = map(lambda x: sorted(x)[:take], roll_results)

        return [x for x in roll_results]

    # Response Handlers

    def get_response(self, message):
        if message.content.lower().startswith('!roll'):
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

        cursedness = 1.0 - (total_curse / total_rolls)

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

        return "Cursedness: `{} / {} = {}` : {}".format(
            total_curse, total_rolls, cursedness, message)

    def get_roll_response(self, message):
        # Remove !roll from content
        reason = None
        split_command = [x.strip() for x in message.content[5:].split('!', 1)]

        roll_clause = re.sub(r'\s+', ' ', split_command[0])
        if len(split_command) > 1:
            reason = split_command[1]

        if not re.fullmatch(COMMAND_EXPR, roll_clause):
            return 'Command did not conform to specs, which do not exist.'

        xforms = re.findall(XFORM_EXPR, roll_clause)

        roll_clause, _ = re.subn(XFORM_EXPR, '', roll_clause)
        print(roll_clause)

        matches = re.findall(ROLL_EXPR, roll_clause)
        rolls, mods = self._split_by_format(matches)

        roll_results = [self.roll(roll) for roll in rolls]

        self._update_curse_data(rolls, roll_results)

        xformed_results = self._apply_xforms(roll_results.copy(), xforms)

        parsed_mods = [x for x in map(int, mods)]

        roll_total = sum(map(sum, xformed_results))
        mod_total = sum(parsed_mods)
        total = roll_total + mod_total

        results_str = ','.join(map(str, xformed_results))
        response = "{} rolled: `{}".format(message.author.nick, results_str)

        if mods:
            response += " + {}".format(' + '.join(map(str, parsed_mods)))
        response += '` '

        response += 'for a total of `{}`'.format(total)

        if reason:
            response += ' to: {}'.format(reason)

        return response
