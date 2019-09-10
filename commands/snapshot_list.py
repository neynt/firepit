import db
import lib
import tabtab

CATEGORY = 'debug'

def run():
    db.c.execute('''
    select s.id, s.time, count(cv.value) num
    from snapshots s
    left join currency_value cv on cv.snapshot = s.id
    group by time
    order by time
    ''')
    currencies = lib.cursor_to_dataframe(db.c).set_index('id')
    db.c.execute('''
    select s.id, s.time, count(av.value) num
    from snapshots s
    left join account_value av on av.snapshot = s.id
    group by time
    order by time
    ''')
    accounts = lib.cursor_to_dataframe(db.c).set_index('id')
    data = []
    for id_, currency in currencies.iterrows():
        data.append((id_, currency.time, currency.num, accounts.loc[id_].num))
    print(tabtab.format(data, headers=['id', 'time', '# currencies', '# accounts']))
