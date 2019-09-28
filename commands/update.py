from commands.account import account_record
from commands.currency import currency_record
from commands.snapshot import snapshot_manual_create, latest_snapshot_id_and_time
from commands.transaction import transaction_loop

import os
import time
import itertools

import pandas as pd

import db
import lib
import config
import tabtab
import modules

def open_browser(fetcher_name, new_window=False):
    fetcher = modules.FETCHERS.get(fetcher_name)
    if not fetcher:
        print(f'Could not find fetcher {fetcher_name}')
        return
    time.sleep(0.1)
    os.system(f'{config.BROWSER_CMD} {"--new-window" if new_window else ""} {fetcher.URL}')

@lib.command(category='tracking')
def update_resume():
    """Allows you to resume from an interrupted update session."""
    snapshots = db.query('''
    select id, time from snapshots
    order by time desc
    limit 2
    ''')
    snapshot_id, snapshot_time = snapshots[0]
    prev_snapshot_id, prev_snapshot_time = snapshots[1]
    print(f'Snapshot for {lib.smart_str(snapshot_time)}')
    # accounts

    accounts = db.query_to_dataframe('''
    select a.id, a.name, av_curr.value curr_value, av_prev.value value, a.currency as curr, a.fetcher
    from accounts a
    left join account_value av_curr on av_curr.id = a.id and av_curr.snapshot = ?
    left join account_value av_prev on av_prev.id = a.id and av_prev.snapshot = ?
    where a.active
    ''', (snapshot_id, prev_snapshot_id))
    accounts.fillna({'fetcher': 'zzz---none---'}, inplace=True)
    groups = accounts.groupby('fetcher')

    fetchers = list(groups.groups.keys())
    fetcher_chunks = list(fetchers[i:i+5] for i in range(0, len(fetchers), 5))

    first = True
    def open_browser_for(fetcher_name):
        nonlocal first
        if fetcher_name == 'zzz---none---':
            return
        open_browser(fetcher_name, new_window=first)
        first = False

    for chunk in fetcher_chunks:
        for fetcher in chunk:
            open_browser_for(fetcher)
        rows = pd.concat([accounts.iloc[groups.groups[fetcher]] for fetcher in chunk])
        for _, account in rows.iterrows():
            account_name = account['name']
            if not pd.isna(account.curr_value):
                print(f'{account_name}: {account.curr_value} {account.curr}')
                continue
            if pd.isna(account.value):
                prompt_text = f'{account_name} ({account.curr})? '
            else:
                prompt_text = f'{account_name} (prev: {account.value} {account.curr})? '
            amount = lib.prompt(prompt_text)
            if not amount:
                if pd.isna(account.value):
                    print('Skipping')
                    continue
                else:
                    print(f'Assuming ({account.value} {account.curr})')
                    amount = account.value
            account_record(account.id, snapshot_id, amount)

            if lib.prompt_confirm('Record transactions?'):
                transaction_loop(account.id)

    # currencies
    currencies = db.query_to_dataframe('''
    select c.symbol, cv_curr.value curr_value, cv_prev.value prev_value, c.name
    from currencies c
    left join currency_value cv_curr on cv_curr.symbol = c.symbol and cv_curr.snapshot = ?
    left join currency_value cv_prev on cv_prev.symbol = c.symbol and cv_prev.snapshot = ?
    where c.active
    ''', (snapshot_id, prev_snapshot_id))
    tabtab.print_dataframe(currencies)
    for _, cur in currencies.iterrows():
        if not pd.isna(cur.curr_value):
            print('{cur.symbol}: {cur.curr_value}')
            continue
        value = input(f'Value of {cur.symbol}? ')
        currency_record(cur.symbol, value)

@lib.command(category='tracking')
def update_new():
    """Creates a new snapshot and opens browser windows."""
    snapshot_manual_create()
    update_resume()
