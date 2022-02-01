from commands.account import account_record
from commands.currency import currency_record
from commands.snapshot import snapshot_manual_create
from commands.transaction import transaction_loop

import pandas as pd

import db
import lib
import tabtab

@lib.command(category='tracking')
def update_resume():
    """Allows you to resume from an interrupted update session."""
    snapshots = db.query('''
    select id, time from snapshots
    order by time desc
    limit 2
    ''')
    snapshot_id, snapshot_time = snapshots[0]
    prev_snapshot_id, _prev_snapshot_time = snapshots[1]
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

    rows = pd.concat([accounts.iloc[groups.groups[fetcher]] for fetcher in fetchers])
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
            print(f'{cur.symbol}: {cur.curr_value}')
            continue
        value = input(f'Value of {cur.symbol}? ')
        currency_record(cur.symbol, value)

@lib.command(category='tracking')
def update_new():
    """Creates a new snapshot and opens browser windows."""
    snapshot_manual_create()
    update_resume()
