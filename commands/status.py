import db
import tabtab
import lib
import pandas as pd

CATEGORY = 'reporting'

def run():
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
    c.execute('''
    select c.symbol, c.name, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    left join currency_value cv2 on (c.symbol = cv2.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null
      and c.active = true
    ''')
    currencies = lib.cursor_to_dataframe(c).set_index('symbol')
    print(tabtab.format_dataframe(currencies))
    print()

    c.execute('''
    select a.id, a.name, av.value, a.currency as curr
    from accounts a
    left join account_value av on av.id = a.id
    left join account_value av2 on (av2.id = av.id and av.snapshot < av2.snapshot)
    where av2.snapshot is null
      and av.value != 0
      and a.active = true
    ''', ())
    accounts = lib.cursor_to_dataframe(c).set_index('id')
    print(tabtab.format_dataframe(accounts))
    print()

    rows = []
    grand_total = 0.0
    accounts = pd.merge(accounts, currencies, left_on='curr', right_on='symbol')
    accounts['value_ref'] = accounts['value_x'] * accounts['value_y']
    for symbol, group in accounts.groupby('curr'):
        total = group.value_x.sum()
        total_ref = group.value_ref.sum()
        rows.append((symbol, total, total_ref))
        grand_total += currencies.loc[symbol].value * total
    baseline_currency = currencies[currencies.value == 1].iloc[0].name
    print(tabtab.format(rows, headers=['curr', 'total', f'(in {baseline_currency})']))
    print()
    print(f'Grand total: {grand_total:.2f} {baseline_currency}')

