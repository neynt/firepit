import pandas as pd

import db
import lib
import tabtab

@lib.command(category='reporting')
def status():
    """Shows status of your accounts."""
    c = db.c
    c.execute('''
    select id, time from snapshots
    order by time desc
    limit 1
    ''')
    snapshot = c.fetchone()

    print(f'Snapshot as of {snapshot[1]}')
    print()

    currencies = db.query_to_dataframe('''
    select c.symbol, c.name, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    left join currency_value cv2 on (c.symbol = cv2.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null
      and c.active = true
    ''').set_index('symbol')
    print(tabtab.format_dataframe(currencies))
    print()

    accounts = db.query_to_dataframe('''
    select a.id, a.name, av.value, a.currency as curr
    from accounts a
    left join account_value av on av.id = a.id
    left join account_value av2 on (av2.id = av.id and av.snapshot < av2.snapshot)
    where av2.snapshot is null
      and av.value != 0
      and a.active = true
    ''', ()).set_index('id')
    print(tabtab.format_dataframe(accounts))
    print()

    rows = []
    grand_total = 0.0
    accounts = pd.merge(accounts, currencies, left_on='curr', right_on='symbol')
    accounts['value_ref'] = accounts['value_x'] * accounts['value_y']
    currs = accounts.groupby('curr').sum()
    del currs['value_y']
    baseline_currency = currencies[currencies.value == 1].iloc[0].name
    print(tabtab.format_dataframe(currs, headers=['curr', 'total', f'(in {baseline_currency}']))
    print()

    print(f'Grand total: {grand_total:.2f} {baseline_currency}')
