from datetime import timedelta

from commands.account import account_values
from commands.currency import currency_values
from commands.transaction import transactions_between

import pandas as pd

import db
import lib
import tabtab

@lib.command(category='reporting')
def status():
    """Shows status of your accounts."""
    last_snapshot_id, last_snapshot_time = db.query_one('''
    select id, time from snapshots
    order by time desc
    limit 1
    ''')

    prev_snapshot_id, prev_snapshot_time = db.query_one('''
    select id, time from snapshots
    where time < ?
    order by time desc
    limit 1
    ''', (last_snapshot_time - timedelta(days=7),))

    print(f'{lib.smart_str(prev_snapshot_time)} - {lib.smart_str(last_snapshot_time)}')
    print()

    currencies = currency_values(last_snapshot_id)
    tabtab.print_dataframe(currencies, drop_index=True)
    print()
    del currencies['name']

    accounts_last = account_values(last_snapshot_id)
    accounts_prev = account_values(prev_snapshot_id)

    txs = transactions_between(prev_snapshot_time, last_snapshot_time)
    txs_by_cat = txs[['category_id', 'amount']].groupby('category_id').sum()
    print(txs_by_cat)

    txs_by_acct = txs[['account_id', 'amount']].groupby('account_id').sum()

    accounts = pd.merge(accounts_last, accounts_prev, how='left', on='id', suffixes=('', '_'))
    accounts['Δ'] = accounts.value - accounts.value_
    accounts = pd.merge(accounts, txs_by_acct, how='outer', left_on='id', right_on='account_id')
    accounts = accounts.rename(columns={'amount': 'tx'})
    accounts = accounts.fillna(value={'tx': 0.0})
    accounts = accounts[['name', 'curr', 'value', 'Δ', 'tx']]
    tabtab.print_dataframe(accounts, drop_index=True)
    print()

    accounts = pd.merge(accounts, currencies, left_on='curr', right_on='symbol', suffixes=('', '_'))
    accounts['value_ref'] = accounts['value'] * accounts['value_']
    currs = accounts.groupby('curr').sum()
    currs = currs[['value', 'value_ref']]
    # Use the currency whose value is 1 as a reference currency.
    # TODO: configurable reference currency
    ref_currency = currencies[currencies.value == 1].iloc[0].symbol
    currs.value_ref = round(currs.value_ref * 100) / 100
    tabtab.print_dataframe(currs, headers=['curr', 'total', f'(in {ref_currency})'])
    print()

    grand_total = currs.value_ref.sum()
    print(f'Grand total: {grand_total:.2f} {ref_currency}')
