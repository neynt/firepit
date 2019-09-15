from collections import defaultdict

import pandas as pd
import prompt_toolkit

import tabtab

COMMANDS = {}
COMMAND_NAMES_BY_CATEGORY = defaultdict(list)
def command(category='debug'):
    def decorator(f):
        command_name = f.__name__.replace('_', '-')
        COMMANDS[command_name] = f
        COMMAND_NAMES_BY_CATEGORY[category].append(command_name)
        return f
    return decorator

def print_cursor(c):
    print(tabtab.format(c.fetchall(), headers=[desc[0] for desc in c.description]))

def cursor_to_dataframe(c):
    return pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])

def prompt(*args):
    return prompt_toolkit.prompt(*args)
