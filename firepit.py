from colorama import Fore, Style
from datetime import datetime, timezone
import importlib
import inspect
import os
import pandas as pd
import readline
import shlex
import sqlite3
import sys

import tabtab
try:
    from config import *
except ModuleNotFoundError:
    from config_example import *

fetcher_memo = {}
def get_fetcher(name):
    if name not in fetcher_memo:
        fetcher_memo[name] = importlib.import_module(f'fetchers.{name}')
    return fetcher_memo[name]

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

def cursor_to_dataframe(c):
    return pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])

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
    select s.id, s.time, count(cv.value) num
    from snapshots s
    left join currency_value cv on cv.snapshot = s.id
    group by time
    order by time
    ''')
    currencies = cursor_to_dataframe(c).set_index('id')
    c.execute('''
    select s.id, s.time, count(av.value) num
    from snapshots s
    left join account_value av on av.snapshot = s.id
    group by time
    order by time
    ''')
    accounts = cursor_to_dataframe(c).set_index('id')
    data = []
    for id_, currency in currencies.iterrows():
        data.append((id_, currency.time, currency.num, accounts.loc[id_].num))
    print(tabtab.format(data, headers=['id', 'time', '# currencies', '# accounts']))

@command
def test_fetcher(name):
    global driver
    driver = make_webdriver()
    print(get_fetcher(name).fetch(driver, **fetcher_credentials[name]))

@command
def snapshot():
    prev_snapshot_id = latest_snapshot_id()
    c.execute('''
    insert into snapshots (time) values (?)
    ''', (datetime.now(timezone.utc),))
    snapshot_id = c.lastrowid

    # accounts
    c.execute('''
    select a.id, a.name, a.currency, av.value, a.fetcher, a.fetcher_param
    from accounts a
    left join account_value av on av.id = a.id
    left join account_value av2 on (av2.id = av.id and av.snapshot < av2.snapshot)
    where av2.snapshot is null and a.active = true
    ''')
    accounts = cursor_to_dataframe(c)
    accounts.fillna({'fetcher': 'none'}, inplace=True)
    groups = accounts.groupby('fetcher')
    for fetcher, _ in groups:
        if fetcher != 'none':
            os.system(f'{browser_cmd} {get_fetcher(fetcher).url}')
    for fetcher, rows in groups:
        for _, a in rows.iterrows():
            if pd.isnull(a.value):
                amount = input(f'{a["name"]} (new, {a.currency})? ')
            else:
                amount = input(f'{a["name"]} (prev: {a.value} {a.currency})? ')
            if not amount:
                print('Assuming ({a.value} {a.currency})')
                amount = a.value
            record(a.id, amount)

    # currencies
    c.execute('''
    select c.symbol, cv.value, c.name
    from currencies c
    left join currency_value cv on cv.symbol = c.symbol
    left join currency_value cv2 on (cv2.symbol = cv.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null and c.active = true
    ''')
    currencies = cursor_to_dataframe(c)
    print(currencies)
    for _, cur in currencies.iterrows():
        value = input(f'Value of {cur.symbol}? ')
        record_currency(cur.symbol, value)

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
def account_fetchers():
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
        print(f'commands: {" ".join(sorted(all_commands))}')
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
