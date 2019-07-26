import sqlite3
import readline
import inspect
import shlex
from datetime import datetime, timezone

from colorama import Fore, Style

import tabtab
from fetchers import capital_one

try:
    from secret import *
except ModuleNotFoundError:
    from secret_example import *

fetchers = {
    'capital_one': capital_one,
}

conn = sqlite3.connect('data.sqlite')
c = conn.cursor()
c.execute('pragma foreign_keys = on;')
conn.commit()
del c

commands = []
def command(f):
    commands.append(f)
    return f

def latest_snapshot_id():
    c.execute('''
    select id, time from snapshots
    order by time desc
    limit 1
    ''')
    result = c.fetchone()
    if not result:
        # We could fail, but it's cleaner to just create one
        new_snapshot()
        return latest_snapshot_id()
    id_, time = result
    return id_

c = None

def print_cursor(c):
    print(tabtab.format(c.fetchall(), headers=[desc[0] for desc in c.description]))

@command
def status():
    """Shows status of your accounts."""
    currencies()
    print()
    snapshot_id = latest_snapshot_id()
    c.execute('''
    select a.id, a.name, av.value, a.currency
    from accounts a
    left join account_value av on av.id = a.id
    left join account_value av2 on (av2.id = av.id and av.snapshot < av2.snapshot)
    where av2.snapshot is null
    ''', ())
    print_cursor(c)

@command
def history():
    """Shows history of an account over time."""
    snapshot_id = latest_snapshot_id()
    c.execute('''
    select a.id, s.time, av.value, a.name, a.currency
    from accounts a
    left join account_value av on av.id = a.id
    left join snapshots s on av.snapshot = s.id
    ''', ())
    print_cursor(c)

@command
def record(account_id, value):
    """Sets the value of the account for the latest snapshot."""
    snapshot_id = latest_snapshot_id()
    c.execute('''
    insert into account_value (id, snapshot, value)
    values (?, ?, ?)
    on conflict (id, snapshot)
    do update set value=?
    ''', (account_id, snapshot_id, value, value))

@command
def new_snapshot():
    c.execute('''
    insert into snapshots (time) values (?)
    ''', (datetime.now(timezone.utc),))

@command
def snapshots():
    c.execute('''
    select * from snapshots
    ''')
    print_cursor(c)

@command
def snapshot():
    prev_snapshot_id = latest_snapshot_id()
    c.execute('''
    insert into snapshots (time) values (?)
    ''', (datetime.now(timezone.utc),))
    snapshot_id = c.lastrowid
    c.execute('''
    select a.id, a.name, a.currency, a.fetcher, a.fetcher_param
    from accounts a
    where active = true
    ''')
    fetcher_cache = {}
    for a_id, name, currency, fetcher, fetcher_param in c.fetchall():
        if fetcher:
            if fetcher not in fetcher_cache:
                fetcher_cache[fetcher] = fetchers[fetcher]()
            amount = fetcher_cache[fetcher][fetcher_param]
        else:
            amount = input(f'{name} ({currency}): ')
        record(a_id, amount)

@command
def accounts():
    c.execute('''
    select name, currency
    from accounts
    order by name
    ''')
    print_cursor(c)

@command
def new_account(name, currency):
    c.execute('''
    insert into accounts (name, currency)
    values (?, ?)
    ''', (name, currency))

@command
def set_fetcher(account_id, fetcher, fetcher_param):
    c.execute('''
    update accounts
    set fetcher=?, fetcher_param=?
    where id=?
    ''', (fetcher, fetcher_param, account_id))

@command
def fetchers():
    c.execute('''
    select * from accounts
    ''')
    print_cursor(c)

@command
def del_account():
    c.execute('''
    select id, name, currency
    from accounts
    ''')
    print(tabtab.format(c.fetchall(), headers=['Id', 'Name', 'Currency']))
    print('Delete which id?')
    id_ = input('> ')
    c.execute('''
    delete from accounts
    where id = ?
    ''', (id_,))

@command
def currencies():
    c.execute('''
    select c.symbol, c.name, cv.snapshot, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    ''')
    print_cursor(c)

@command
def new_currency(symbol, name):
    c.execute('''
    insert into currencies (symbol, name)
    values (?, ?)
    ''', (symbol, name))
    currencies()

@command
def del_currency(symbol):
    c.execute('''
    delete from currencies
    where symbol = ?
    ''', (symbol,))
    currencies()

@command
def record_currency(symbol, value):
    """Sets the value of the account for the latest snapshot."""
    snapshot_id = latest_snapshot_id()
    c.execute('''
    insert into currency_value (symbol, snapshot, value)
    values (?, ?, ?)
    on conflict (symbol, snapshot)
    do update set value=?
    ''', (symbol, snapshot_id, value, value))

@command
def help(name=None):
    if not name:
        print(f'commands: {" ".join(all_commands)}')
        return
    f = name_to_f.get(name)
    if f:
        print(inspect.getdoc(f) or f'No docs for {name}')
    else:
        print('unknown command')

all_commands = [f.__name__ for f in commands]
name_to_f = {f.__name__: f for f in commands}

def main():
    print(f'\n  {Fore.RED}.{Fore.YELLOW}~{Fore.RED}.{Style.RESET_ALL} {Style.BRIGHT}{Fore.WHITE}firepit{Style.RESET_ALL}\n')
    while True:
        args = shlex.split(input('> '))
        if not args: continue
        f = name_to_f.get(args[0])
        args = args[1:]
        if not f:
            print('command not found')
            continue
        try:
            sig = inspect.signature(f)
            params = [(k, v) for k, v in sig.parameters.items() if v.default == inspect.Parameter.empty]
            if len(params) > len(args):
                for i, (name, _) in enumerate(params):
                    if i < len(args):
                        print(f'{name}: {args[i]}')
                    else:
                        args.append(input(f'{name}: '))
            global c
            c = conn.cursor()
            f(*args)
            conn.commit()
        except KeyboardInterrupt as e:
            print('Cancelled.')
            conn.rollback()
        except sqlite3.IntegrityError as e:
            print(e)
            conn.rollback()

if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('Bye.')
