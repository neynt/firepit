from collections import defaultdict

import numpy as np
import pandas as pd
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError

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

class ListValidator(Validator):
    def __init__(self, items):
        self.items = items

    def validate(self, document):
        if document.text not in self.items:
            raise ValidationError(message='Not a valid choice',
                                  cursor_position=len(document.text))

class CommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        current = document.current_line_before_cursor
        for name in COMMANDS.keys():
            if name.startswith(current):
                yield Completion(name, start_position=-len(current))
        # TODO: Complete command parameters

def smart_str(item):
    """Convert to string, with smart handling for certain types."""
    plain = str(item)
    formatted = plain
    if type(item) in [float, np.float64]:
        if item != 0.0:
            for decimals in [0, 2, 3, 4, 5, 6, 7, 8]:
                s = ('{:.%df}' % decimals).format(item)
                item_ = float(s)
                diff = abs(item - item_)
                if diff < 0.1**(decimals + 2) and diff / item < 0.01:
                    plain = s
                    break
            if item < 0:
                formatted = f'<ansired>{plain}</ansired>'
            elif item > 0:
                formatted = f'<ansigreen>{plain}</ansigreen>'
    elif type(item) in [int, np.int64]:
        formatted = f'<ansiblue>{plain}</ansiblue>'
    elif type(item) == pd.Timestamp:
        plain = item.strftime("%Y %b %d %H:%M")
        formatted = plain
    elif type(item) == bool:
        if item:
            plain = '✔'
            formatted = f'<ansigreen>{plain}</ansigreen>'
        else:
            plain = '✘'
            formatted = f'<ansired>{plain}</ansired>'
    elif type(item) == str:
        pass
    elif item == None:
        plain = 'n/a'
        formatted = f'<ansiblack>{plain}</ansiblack>'
    else:
        print('note: unhandled type', type(item))
    return plain, formatted

