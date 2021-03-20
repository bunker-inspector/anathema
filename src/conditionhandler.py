"""
Gives information of Pathfinder 2e conditions
"""

from handler import Handler


def read_conditions(filepath: str):
    """Converts conditions file to dictionary"""
    with open(filepath, 'r') as conditions_file:
        conditions = {}
        current_condition_name = line = conditions_file.readline().strip(
        ).lower()
        current_condition_description = []
        while line:
            if line.startswith('"'):
                current_condition_description.append(line.replace('"', ''))
            else:
                current_condition_name = line.strip().lower()
                conditions[current_condition_name] = '\n'.join(
                    current_condition_description)
                current_condition_description = []
            line = conditions_file.readline()
    return conditions


class ConditionHandler(Handler):
    """Handles conditions commands"""
    def __init__(self, filepath='conditions.txt'):
        self.conditions = read_conditions(filepath)

    async def process(self, message):
        """Process condition command"""
        tokens = message.content.split()
        if tokens[0] != '!conditions' or len(tokens) > 2:
            return

        if len(tokens) == 1:
            return await message.channel.send('\n'.join(
                sorted(list(map(lambda x: x.capitalize(), self.conditions)))))

        await message.channel.send(
            self.conditions.get(tokens[1].strip().lower(),
                                'Condition unkown.'))
