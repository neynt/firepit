from commands.account import prompt_account
from commands.category import prompt_category

import inspect
import shlex
import sqlite3
import pandas as pd

from colorama import Fore, Back, Style

import db
import lib
import modules
import tabtab

def main():
    """Main entry point and input handling loop."""
    print(f'\n  {Fore.RED}.{Style.BRIGHT}{Fore.YELLOW}~{Style.NORMAL}{Fore.RED}.{Style.RESET_ALL} '
          f'{Style.BRIGHT}{Fore.YELLOW}firepit{Fore.RESET}{Back.RESET}  '
          f'{Fore.RESET}personal finance with a pit'
          f'{Style.RESET_ALL}\n')
    while True:
        line = lib.prompt_cmd('» ', completer=lib.CommandCompleter(), complete_while_typing=True)
        args = shlex.split(line)
        if not args:
            continue
        f = lib.COMMANDS.get(args[0])
        args = args[1:]
        if not f:
            print('command not found')
            continue
        try:
            sig = inspect.signature(f)
            params = [(k, v) for k, v in sig.parameters.items()
                      if v.default == inspect.Parameter.empty]
            if len(params) > len(args):
                for i, (name, _) in enumerate(params):
                    if i < len(args):
                        print(f'{name}: {args[i]}')
                    else:
                        if name == 'account_id':
                            args.append(prompt_account())
                        elif 'category_id' in name:
                            args.append(prompt_category())
                        elif name == 'day':
                            args.append(lib.prompt_datetime(f'{name}: '))
                        else:
                            args.append(lib.prompt(f'{name}: '))
            db.begin()
            result = f(*args)
            if isinstance(result, pd.DataFrame):
                tabtab.print_dataframe(result)
            elif result == None:
                pass
            else:
                print(f'Command returned {type(result)}: {result}')
            db.commit()
        except KeyboardInterrupt as e:
            print('Cancelled.')
            db.rollback()
        except sqlite3.IntegrityError as e:
            print(e)
            db.rollback()

if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('Bye.')
