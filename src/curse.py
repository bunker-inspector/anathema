"""
Utilities for tracking roll statistics.
"""

from kv import KV

KEY = 'curse'


def CurseManager():
    """Entity that will track statistics when given roll outcomes"""
    def __init__(self, storage: KV):
        self.storage = storage

    def get_cursedness(self):
        """Returns the roll average vs potential"""
        curse_data = self.storage.get('roll')

        if not curse_data:
            return None

        total_curse = curse_data['total_curse']
        total_rolls = curse_data['total_rolls']

        return 1.0 - (total_curse / total_rolls)

    def update_curse(self, rolls, results):
        """Updates curse value with given roll results"""
        num_rolls = sum(map(len, results))
        cursedness = self.get_cursedness(rolls, results)

        curse_data = self.storage.get(KEY)

        if not curse_data:
            curse_data = {'total_curse': 0.0, 'total_rolls': 0}

        curse_data['total_curse'] = curse_data['total_curse'] + cursedness
        curse_data['total_rolls'] = curse_data['total_rolls'] + num_rolls

        self.storage.put(KEY, curse_data)

    def purify(self):
        """Clears curse"""
        self.storage.delete(KEY)

    def _calculate_cursedness(rolls):
        """Calculates the cursedness of a single roll outcome"""
        total_cursedness = 0.0
        for idx, roll in enumerate(rolls):
            roll_potential = int(roll.split('d')[1])
            results_in_set = rolls[idx]
            for result in results_in_set:
                cursedness = 0.5 if roll_potential == 1 else (result - 1) / (
                    roll_potential - 1)
                total_cursedness += cursedness
        return total_cursedness
