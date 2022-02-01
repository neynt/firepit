import html
import inspect
from datetime import datetime, date
from collections import defaultdict

import numpy as np
import pandas as pd
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError

import amortize

COMMANDS = {}
COMMAND_NAMES_BY_CATEGORY = defaultdict(list)
def command(category='debug'):
    def decorator(f):
        command_name = f.__name__.replace('_', '-')
        COMMANDS[command_name] = f
        COMMAND_NAMES_BY_CATEGORY[category].append(command_name)
        return f
    return decorator

PROMPTERS = {}
def prompter(arg_name):
    def decorator(f):
        PROMPTERS[arg_name] = f
        return f
    return decorator

def cursor_to_dataframe(c):
    return pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])

class CommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        current = document.current_line_before_cursor
        for name in COMMANDS.keys():
            if name.startswith(current):
                yield Completion(name, start_position=-len(current))
        # TODO: Complete command parameters

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

def prompt_list(items, *args):
    items = sorted(items, key=len)
    completer = ListCompleter(items)
    validator = ListValidator(items)
    res = prompt(*args,
                 completer=completer,
                 validator=validator,
                 complete_while_typing=True,
                 validate_while_typing=False)
    return res

def prompt_list_nonstrict(items, *args):
    items = sorted(items, key=len)
    completer = ListCompleter(items)
    res = prompt(*args,
                 completer=completer,
                 complete_while_typing=True)
    return res

class AmortizeValidator(Validator):
    def validate(self, document):
        try:
            amortize.of_string(document.text)
        except ValueError:
            raise ValidationError(message='Invalid amortization',
                                  cursor_position=len(document.text))

def prompt_amortize():
    # TODO: make this format more discoverable
    validator = AmortizeValidator()
    print('amortization format: [linear|point] NUMBER days')
    res = prompt(f'amortization: ',
                 validator=validator,
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

@prompter('day')
def prompt_date(*args):
    res = prompt(*args,
                 validator=DatetimeValidator(),
                 validate_while_typing=True)
    return parse_datetime(res).date()

def prompt_confirm(prompt_word):
    return prompt_list(['y', 'n'], f'{prompt_word} (y/n): ') == 'y'

class IntValidator(Validator):
    def validate(self, document):
        pos = len(document.text)
        try:
            int(document.text)
        except ValueError as e:
            raise ValidationError(message=str(e), cursor_position=pos)

def prompt_int(*args):
    res = prompt(*args,
                 validator=IntValidator(),
                 validate_while_typing=True)
    return int(res)

class FloatValidator(Validator):
    def validate(self, document):
        pos = len(document.text)
        try:
            float(document.text)
        except ValueError as e:
            raise ValidationError(message=str(e), cursor_position=pos)

def prompt_float(*args):
    res = prompt(*args,
                 validator=FloatValidator(),
                 validate_while_typing=True)
    return float(res)

def prompt_day_desc_price(*args):
    def get_parts(s):
        day, desc, price = map(str.strip, s.split(';'))
        day = parse_datetime(day).date()
        price = float(price)
        return day, desc, price
    class Validate(Validator):
        def validate(self, document):
            pos = len(document.text)
            try:
                get_parts(document.text)
            except ValueError as e:
                raise ValidationError(message=str(e), cursor_position=pos)
    res = prompt(*args,
                 validator=Validate(),
                 validate_while_typing=True)
    return get_parts(res)

def format_str(item):
    """Convert to string, with smart handling for certain types."""
    plain = str(item)
    formatted = html.escape(plain)
    if item == None or pd.isna(item):
        plain = 'n/a'
        formatted = f'<ansiblack>{plain}</ansiblack>'
    elif type(item) in [float, np.float64]:
        plain = '{:.2f}'.format(item)
        formatted = plain
        if item != 0.0:
            for decimals in [2, 3, 4, 5, 6, 7, 8]:
                s = ('{:.%df}' % decimals).format(item)
                diff = abs(item - float(s))
                if diff < 0.1**(decimals + 3) and diff / item < 0.00001:
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
    elif type(item) == date:
        pass
    elif type(item) == str:
        pass
    else:
        print('note: unhandled type', type(item))
    return plain, formatted

def smart_str(item):
    return format_str(item)[1]

def call_via_prompts(f, *args, echo_passed=False, **kwargs):
    args = list(args)
    sig = inspect.signature(f)
    params = [(k, v) for k, v in sig.parameters.items()
              if v.default == inspect.Parameter.empty]
    if len(params) > len(args):
        for i, (name, param) in enumerate(params):
            if i < len(args) or name in kwargs:
                if echo_passed:
                    print(f'{name}: {args[i]}')
            elif name in PROMPTERS:
                args.append(PROMPTERS[name](f'{name}: '))
            elif param.default != inspect.Parameter.empty:
                if echo_passed:
                    print(f'assuming {name}: {param.default}')
            else:
                args.append(prompt(f'{name}: '))
    return f(*args, **kwargs)

def call_via_comma_separated(f, *args, **kwargs):
    args = list(args)
    sig = inspect.signature(f)
    params = [(k, v) for k, v in sig.parameters.items()
              if v.default == inspect.Parameter.empty]
    if len(params) > len(args):
        for i, (name, param) in enumerate(params):
            if i < len(args) or name in kwargs:
                if echo_passed:
                    print(f'{name}: {args[i]}')
            elif name in PROMPTERS:
                args.append(PROMPTERS[name](f'{name}: '))
            elif param.default != inspect.Parameter.empty:
                if echo_passed:
                    print(f'assuming {name}: {param.default}')
            else:
                args.append(prompt(f'{name}: '))
    return f(*args, **kwargs)
