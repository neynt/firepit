from datetime import datetime
from collections import defaultdict

import numpy as np
import pandas as pd
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError

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

prompt_session_cmd = PromptSession()
def prompt_cmd(*args, **kwargs):
    return prompt_session_cmd.prompt(*args, **kwargs)

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

def prompt_list(items, prompt_word):
    completer = ListCompleter(items)
    validator = ListValidator(items)
    res = prompt(f'{prompt_word}: ',
                 completer=completer,
                 validator=validator,
                 complete_while_typing=True,
                 validate_while_typing=False)
    return res

def parse_datetime_fragment(fragment):
    result = []
    result.append(('year', datetime.now().year))
    formats = [
        ('%Y-%m-%d', ['year', 'month', 'day']),
        ('%Y/%m/%d', ['year', 'month', 'day']),
        ('%b', ['month']),
        ('%B', ['month']),
        ('%H:%M', ['hour', 'minute']),
    ]
    for fmt, parts in formats:
        try:
            dt = datetime.strptime(fragment, fmt)
            for part in parts:
                result.append((part, getattr(dt, part)))
        except ValueError:
            pass
    try:
        as_int = int(fragment)
        if as_int >= 1000:
            result.append(('year', as_int))
        if 1 <= as_int <= 31:
            result.append(('day', as_int))
    except ValueError:
        pass
    return result

def parse_datetime(s):
    datetime_parts = []
    for fragment in s.split():
        parts = parse_datetime_fragment(fragment)
        if not parts:
            raise ValueError(f'Could not parse datetime fragment {fragment}')
        datetime_parts.extend(parts)
    return datetime(**{part: value for part, value in datetime_parts})

class DatetimeValidator(Validator):
    def validate(self, document):
        pos = len(document.text)
        try:
            parse_datetime(document.text)
        except (ValueError, TypeError) as e:
            raise ValidationError(message=str(e), cursor_position=pos)

def prompt_datetime(*args):
    res = prompt(*args, validator=DatetimeValidator(),
                 validate_while_typing=True)
    return parse_datetime(res)

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
    elif type(item) in [pd.Timestamp, datetime]:
        if item.year != datetime.now().year:
            plain = item.strftime("%Y %b %d %H:%M")
        else:
            plain = item.strftime("%b %d %H:%M")
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
