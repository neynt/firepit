from commands.account import prompt_account
from commands.category import prompt_category

import inspect
import shlex
import sqlite3
import pandas as pd

from colorama import Fore, Back, Style

import db
import lib
import tabtab
import modules
import amortize

def main():
    """Main entry point and input handling loop."""
    print(f'\n  {Fore.RED}.{Style.BRIGHT}{Fore.YELLOW}~{Style.NORMAL}{Fore.RED}.{Style.RESET_ALL} '
          f'{Style.BRIGHT}{Fore.YELLOW}firepit{Fore.RESET}{Back.RESET}  '
          f'{Fore.RESET}personal finance with a pit'
          f'{Style.RESET_ALL}\n')
    while True:
        line = lib.prompt_cmd('» ', completer=lib.CommandCompleter(), complete_while_typing=True)
        try:
            args = shlex.split(line)
        except ValueError as e:
            print(e)
            continue
        if not args:
            continue
        f = lib.COMMANDS.get(args[0])
        args = args[1:]
        if not f:
            print('command not found')
            continue
        try:
            db.begin()
            result = lib.call_via_prompts(f, *args)
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
