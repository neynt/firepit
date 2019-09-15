import inspect
import shlex
import sqlite3

from colorama import Fore, Back, Style

import db
import lib
import modules

def main():
    """Main entry point and input handling loop."""
    print(f'\n  {Fore.RED}.{Style.BRIGHT}{Fore.YELLOW}~{Style.NORMAL}{Fore.RED}.{Style.RESET_ALL} '
          f'{Style.BRIGHT}{Fore.YELLOW}firepit{Fore.RESET}{Back.RESET}  '
          f'{Fore.RESET}personal finance with a pit'
          f'{Style.RESET_ALL}\n')
    while True:
        line = lib.prompt('» ')
        args = shlex.split(line)
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
                        args.append(lib.prompt(f'{name}: '))
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
