from collections import defaultdict
import inspect

import lib
import modules

# unused
def print_subtree(children, indent=0):
    commands = []
    by_prefix = defaultdict(list)
    for child in children:
        parts = child.split('-', 1)
        if len(parts) == 1:
            commands.append(child)
        else:
            by_prefix[parts[0]].append(parts[1])

    for command in commands:
        print(' ' * indent + command)
    for prefix, rest in by_prefix.items():
        print(' ' * indent + prefix + '-')
        print_subtree(rest, indent=indent + 2)

@lib.command(category='general')
def help(cmd_name=None):
    """Shows a list of commands, or help for a specific command."""
    if cmd_name:
        f = lib.COMMANDS.get(cmd_name)
        if f:
            print(inspect.getdoc(f.run) or f'No doc for {cmd_name}')
        else:
            print('unknown command')
    else:
        for category, names in lib.COMMAND_NAMES_BY_CATEGORY.items():
            if category == 'debug':
                print(f'{category}: (hidden)')
                continue
            print(category + ':')
            for name in sorted(names):
                print('  ' + name)
