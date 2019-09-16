from datetime import datetime, timezone

import db
import lib
import tabtab

@lib.command()
def latest_snapshot_id():
    result = db.query_one('''
    select id, time from snapshots
    order by time desc
    limit 1
    ''')
    if not result:
        # We could fail, but it's cleaner to just create one
        snapshot_manual_create()
        return latest_snapshot_id()
    id_, time = result
    return id_

@lib.command()
def snapshot_list():
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
    tabtab.print_table(data, headers=['id', 'time', '# currencies', '# accounts'])

@lib.command()
def snapshot_manual_create():
    db.execute('''
    insert into snapshots (time) values (?)
    ''', (datetime.now(timezone.utc),))
