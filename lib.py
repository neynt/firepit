from collections import defaultdict

import pandas as pd
from prompt_toolkit import PromptSession

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

def prompt(*args):
    return prompt_session.prompt(*args)
