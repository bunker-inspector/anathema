from handler import Handler
import kv
import json
import re

class CommandHandler(Handler):
    command_key = kv.to_key(b'commands')

    def __init__(self, r, handlers):
        self.r = r
        self.handlers = handlers

        commands = r.get(self.command_key) or '{}'
        self.commands = json.loads(commands)

    def _extract_command(self, message):
        first_space_idx = message.content.find(' ')
        command_end = first_space_idx if first_space_idx > 0 else len(message.content)
        return message.content[1:command_end]

    def accepts(self, message):
        if message.content.startswith('!set-command'):
            return True
        else:
            command = self._extract_command(message)
            author_commands = self.commands.get(str(message.author.id), {})
            return bool(author_commands.get(command, False))

    def get_response(self, message):
        if message.content.startswith('!set-command'):
            return self.get_set_command_response(message)
        else:
            return self.process_user_command(message)

    def get_set_command_response(self, message):
        command_clause_end = message.content.find('::')
        command_clause = message.content[12:command_clause_end].strip()
        if not re.match(r'[a-zA-Z0-9\-_]+', command_clause):
            return "Command can only be alphanumber characters, -, and _"

        command = message.content[command_clause_end+2:].strip()

        author_commands = self.commands.get(message.author.id, {})
        author_commands[command_clause] = command

        self.commands[str(message.author.id)] = author_commands
        print(self.commands)

        self.r.put(self.command_key, json.dumps(self.commands).encode('UTF-8'))

        return '{} registered command: `!{}` -> `{}`'.format(message.author.name, command_clause, command)

    def process_user_command(self, message):
        command = self._extract_command(message)
        mapping = self.commands[str(message.author.id)][command]

        command_input = message.content.strip()
        args = command_input[command_input.find(' '):].strip()

        new_message = mapping.replace('{}', args, 1)
        message.content = new_message

        for handler in self.handlers:
            if handler.accepts(message):
                return handler.get_response(message)

        return False

