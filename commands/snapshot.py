from datetime import datetime, timezone
import os

import pandas as pd

from commands import record, currency_record
import config
import db
import lib
import modules

CATEGORY = 'tracking'

def run():
    """Creates a new snapshot and opens browser windows."""
    c = db.c
    prev_snapshot_id = lib.latest_snapshot_id()
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
    accounts = lib.cursor_to_dataframe(c)
    accounts.fillna({'fetcher': 'none'}, inplace=True)
    groups = accounts.groupby('fetcher')
    if config.BROWSER_CMD in ['firefox']:
        os.system(f'{config.BROWSER_CMD} --new-window')
    for fetcher, _ in groups:
        if fetcher != 'none':
            os.system(f'{config.BROWSER_CMD} {modules.FETCHERS.get(fetcher).url}')
    for fetcher, rows in groups:
        for _, account in rows.iterrows():
            if pd.isnull(account.value):
                amount = input(f'{account["name"]} (new, {account.currency})? ')
            else:
                amount = input(f'{account["name"]} (prev: {account.value} {account.currency})? ')
            if not amount:
                print(f'Assuming ({account.value} {account.currency})')
                amount = account.value
            record.run(account.id, amount)

    # currencies
    c.execute('''
    select c.symbol, cv.value, c.name
    from currencies c
    left join currency_value cv on cv.symbol = c.symbol
    left join currency_value cv2 on (cv2.symbol = cv.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null and c.active = true
    ''')
    currencies = lib.cursor_to_dataframe(c)
    print(currencies)
    for _, cur in currencies.iterrows():
        value = input(f'Value of {cur.symbol}? ')
        currency_record.run(cur.symbol, value)

