import json
from kv import KV


def CurseManager():
    KEY = 'curse'

    def __init__(self, kv: KV):
        self.kv = kv

    def get_cursedness(self):
        curse_data = self.kv.get('roll')

        if not curse_data:
            None

        total_curse = curse_data['total_curse']
        total_rolls = curse_data['total_rolls']

        return 1.0 - (total_curse / total_rolls)

    def update_curse(self, rolls, results):
        num_rolls = sum(map(len, results))
        cursedness = self._get_cursedness(rolls, results)

        curse_data = self.kv.get(KEY)

        if not curse_data:
            curse_data = {'total_curse': 0.0, 'total_rolls': 0}

        curse_data['total_curse'] = curse_data['total_curse'] + cursedness
        curse_data['total_rolls'] = curse_data['total_rolls'] + num_rolls

        self.kv.put(KEY, curse_data)

    def purify(self):
        self.kv.delete(KEY)

    def _calculate_cursedness(self, rolls, results):
        total_cursedness = 0.0
        for idx, roll in enumerate(rolls):
            roll_potential = int(roll.split('d')[1])
            results_in_set = rolls[idx]
            for result in results_in_set:
                cursedness = 0.5 if roll_potential == 1 else (result - 1) / (
                    roll_potential - 1)
                total_cursedness += cursedness
        return total_cursedness
