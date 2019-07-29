from collections import defaultdict
from colorama import Fore, Style
from datetime import datetime, timezone
import importlib
import inspect
import numpy as np
import os
import pandas as pd
import readline
import shlex
import sqlite3
import sys
import textwrap

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
command_names = []
command_by_name = {}
command_categories = defaultdict(list)
def command(cat):
    def fun(f):
        commands.append(f)
        command_names.append(f.__name__)
        command_by_name[f.__name__] = f
        command_categories[cat].append(f.__name__)
        return f
    return fun

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

@command('reporting')
def status():
    """Shows status of your accounts."""
    c.execute('''
    select id, time from snapshots
    order by time desc
    limit 1
    ''')
    snapshot = c.fetchone()
    print(f'Snapshot as of {snapshot[1]}')
    print()
    c.execute('''
    select c.symbol, c.name, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    left join currency_value cv2 on (c.symbol = cv2.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null
      and c.active = true
    ''')
    global currencies
    currencies = cursor_to_dataframe(c).set_index('symbol')
    print(tabtab.format_dataframe(currencies))
    print()
    snapshot_id = latest_snapshot_id()
    c.execute('''
    select a.id, a.name, av.value, a.currency
    from accounts a
    left join account_value av on av.id = a.id
    left join account_value av2 on (av2.id = av.id and av.snapshot < av2.snapshot)
    where av2.snapshot is null
      and av.value > 0
      and a.active = true
    ''', ())
    global accounts
    accounts = cursor_to_dataframe(c).set_index('id')
    print(tabtab.format_dataframe(accounts))
    print()

    global rows
    rows = []
    grand_total = 0.0
    for symbol, group in accounts.groupby('currency'):
        total = group.value.sum()
        rows.append((symbol, total))
        grand_total += currencies.loc[symbol].value * total
    baseline_currency = currencies[currencies.value == 1].iloc[0].name
    print(tabtab.format(rows, headers=['currency', 'total']))
    print()
    print(f'Grand total: {grand_total:.2f} {baseline_currency}')

@command('reporting')
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

@command('tracking')
def record(account_id, value):
    """Sets the value of the account for the latest snapshot."""
    snapshot_id = latest_snapshot_id()
    c.execute('''
    insert into account_value (id, snapshot, value)
    values (?, ?, ?)
    on conflict (id, snapshot)
    do update set value=?
    ''', (account_id, snapshot_id, value, value))

@command('debug')
def new_snapshot():
    c.execute('''
    insert into snapshots (time) values (?)
    ''', (datetime.now(timezone.utc),))

@command('debug')
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

@command('debug')
def test_fetcher(name):
    global driver
    driver = make_webdriver()
    print(get_fetcher(name).fetch(driver, **fetcher_credentials[name]))

@command('tracking')
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
    if browser_cmd in ['firefox']:
        os.system(f'{browser_cmd} --new-window')
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

@command('reporting')
def accounts():
    c.execute('''
    select * from accounts order by name
    ''')
    print_cursor(c)

@command('setup')
def new_account(name, currency):
    c.execute('''
    insert into accounts (name, currency) values (?, ?)
    ''', (name, currency))

@command('debug')
def mod_account(account_id, prop_name, value):
    c.execute(f'''
    update accounts
    set {prop_name}=?
    where id=?
    ''', (value, account_id))

@command('setup')
def set_fetcher(account_id, fetcher, fetcher_param):
    mod_account(account_id, 'fetcher', fetcher)
    mod_account(account_id, 'fetcher_param', fetcher_param)

@command('setup')
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

@command('reporting')
def currencies():
    c.execute('''
    select c.symbol, c.name, c.active, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    left join currency_value cv2 on (c.symbol = cv2.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null
      and c.active = true
    ''')
    print_cursor(c)

@command('setup')
def new_currency(symbol, name):
    c.execute('''
    insert into currencies (symbol, name)
    values (?, ?)
    ''', (symbol, name))
    currencies()

@command('setup')
def del_currency(symbol):
    c.execute('''
    delete from currencies
    where symbol = ?
    ''', (symbol,))
    currencies()

@command('setup')
def record_currency(symbol, value):
    """Sets the value of the account for the latest snapshot."""
    snapshot_id = latest_snapshot_id()
    c.execute('''
    insert into currency_value (symbol, snapshot, value)
    values (?, ?, ?)
    on conflict (symbol, snapshot)
    do update set value=?
    ''', (symbol, snapshot_id, value, value))

@command('general')
def help(name=None):
    if not name:
        for cat in ['general', 'setup', 'tracking', 'reporting', 'debug']:
            cmds = command_categories[cat]
            print(textwrap.fill(cat + ': ' + ', '.join(cmds)))
        return
    f = command_by_name.get(name)
    if f:
        print(inspect.getdoc(f) or f'No docs for {name}')
    else:
        print('unknown command')

def main():
    print(f'\n  {Fore.RED}.{Fore.YELLOW}~{Fore.RED}.{Style.RESET_ALL} {Style.BRIGHT}{Fore.WHITE}firepit{Style.RESET_ALL}\n')
    while True:
        args = shlex.split(input('> '))
        if not args: continue
        f = command_by_name.get(args[0])
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
