from commands.account import account_record
from commands.currency import currency_record
from commands.snapshot import snapshot_manual_create

import os

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
    os.system(f'{config.BROWSER_CMD} {"--new-window" if new_window else ""} {fetcher.URL}')

@lib.command(category='tracking')
def update():
    """Creates a new snapshot and opens browser windows."""
    snapshot_manual_create()

    # accounts
    accounts = db.query_to_dataframe('''
    select a.id, a.name, a.currency, av.value, a.fetcher, a.fetcher_param
    from accounts a
    left join account_value av on av.id = a.id
    left join account_value av2 on (av2.id = av.id and av.snapshot < av2.snapshot)
    where av2.snapshot is null and a.active = true
    ''')
    accounts.fillna({'fetcher': 'zzz---none---'}, inplace=True)
    groups = accounts.groupby('fetcher')
    first = True
    for fetcher_name, rows in groups:
        if fetcher_name != 'zzz---none---':
            open_browser(fetcher_name, new_window=first)
        for _, account in rows.iterrows():
            first = False
            if pd.isna(account.value):
                amount = lib.prompt(f'{account["name"]} ({account.currency})? ')
            else:
                amount = lib.prompt(f'{account["name"]} (prev: {account.value} {account.currency})? ')
            if not amount:
                if pd.isna(account.value):
                    print('Skipping')
                    continue
                else:
                    print(f'Assuming ({account.value} {account.currency})')
                    amount = account.value
            account_record(account.id, amount)

    # currencies
    currencies = db.query_to_dataframe('''
    select c.symbol, cv.value, c.name
    from currencies c
    left join currency_value cv on cv.symbol = c.symbol
    left join currency_value cv2 on (cv2.symbol = cv.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null and c.active = true
    ''')
    print(tabtab.format_dataframe(currencies))
    for _, cur in currencies.iterrows():
        value = input(f'Value of {cur.symbol}? ')
        currency_record(cur.symbol, value)
