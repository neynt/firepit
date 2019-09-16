from collections import defaultdict

import pandas as pd
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

import tabtab

prompt_session = PromptSession()

COMMANDS = {}
COMMAND_NAMES_BY_CATEGORY = defaultdict(list)
def command(category='debug'):
    def decorator(f):
        command_name = f.__name__.replace('_', '-')
        COMMANDS[command_name] = f
        COMMAND_NAMES_BY_CATEGORY[category].append(command_name)
        return f
    return decorator

def cursor_to_dataframe(c):
    return pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])

def prompt(*args, **kwargs):
    return prompt_session.prompt(*args, **kwargs)

class ListCompleter(Completer):
    def __init__(self, items):
        self.items = items

    def get_completions(self, document, complete_event):
        current = document.current_line_before_cursor
        for item in self.items:
            if item.startswith(current):
                yield Completion(item, start_position=-len(current))

class CommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        current = document.current_line_before_cursor
        for name in COMMANDS.keys():
            if name.startswith(current):
                yield Completion(name, start_position=-len(current))
        # TODO: Complete command parameters
