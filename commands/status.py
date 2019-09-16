from commands.account import account_values
from commands.currency import currency_values

import pandas as pd

import db
import lib
import tabtab

@lib.command(category='reporting')
def status():
    """Shows status of your accounts."""
    snapshot = db.query_one('''
    select id, time from snapshots
    order by time desc
    limit 1
    ''')

    print(f'Snapshot as of {snapshot[1]}')
    print()

    currencies = currency_values()
    tabtab.print_dataframe(currencies)
    print()

    accounts = account_values()
    tabtab.print_dataframe(accounts)
    print()

    accounts = pd.merge(accounts, currencies, left_on='curr', right_on='symbol')
    accounts['value_ref'] = accounts['value_x'] * accounts['value_y']
    currs = accounts.groupby('curr').sum()
    del currs['value_y']

    # Use the currency whose value is 1 as a reference currency.
    # TODO: configurable reference currency
    ref_currency = currencies[currencies.value == 1].iloc[0].name
    tabtab.print_dataframe(currs, headers=['curr', 'total', f'(in {ref_currency})'])
    print()

    grand_total = currs.value_ref.sum()
    print(f'Grand total: {grand_total:.2f} {ref_currency}')
