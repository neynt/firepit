import inspect
import shlex
import sqlite3

from colorama import Fore, Style

import db
import modules

def main():
    """Main entry point and input handling loop."""
    print(f'\n  {Fore.RED}.{Fore.YELLOW}~{Fore.RED}.{Style.RESET_ALL} '
          f'{Style.BRIGHT}{Fore.WHITE}firepit{Style.RESET_ALL}\n')
    while True:
        args = shlex.split(input('> '))
        if not args:
            continue
        module = modules.COMMANDS.get(args[0])
        args = args[1:]
        if not module:
            print('command not found')
            continue
        try:
            sig = inspect.signature(module.run)
            params = [(k, v) for k, v in sig.parameters.items()
                      if v.default == inspect.Parameter.empty]
            if len(params) > len(args):
                for i, (name, _) in enumerate(params):
                    if i < len(args):
                        print(f'{name}: {args[i]}')
                    else:
                        args.append(input(f'{name}: '))
            db.c = db.conn.cursor()
            module.run(*args)
            db.conn.commit()
        except KeyboardInterrupt as e:
            print('Cancelled.')
            db.conn.rollback()
        except sqlite3.IntegrityError as e:
            print(e)
            db.conn.rollback()

if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('Bye.')
