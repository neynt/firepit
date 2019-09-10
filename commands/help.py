from collections import defaultdict
import inspect

import modules

CATEGORY = 'general'

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
        print_subtree(rest, indent = indent + 2)

def run(cmd_name=None):
    """Shows a list of commands, or help for a specific command."""
    if cmd_name:
        f = modules.COMMANDS.get(cmd_name)
        if f:
            print(inspect.getdoc(f.run) or f'No doc for {cmd_name}')
        else:
            print('unknown command')
    else:
        categories = defaultdict(list)
        for name, command in modules.COMMANDS.items():
            categories[command.CATEGORY].append(name)
        for CATEGORY, names in categories.items():
            print(CATEGORY)
            for name in sorted(names):
                print('  ' + name)
