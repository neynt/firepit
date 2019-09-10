import db
import tabtab
import pandas as pd

from commands import snapshot_manual_create

def print_cursor(c):
    print(tabtab.format(c.fetchall(), headers=[desc[0] for desc in c.description]))

def cursor_to_dataframe(c):
    return pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])

def latest_snapshot_id():
    db.c.execute('''
    select id, time from snapshots
    order by time desc
    limit 1
    ''')
    result = db.c.fetchone()
    if not result:
        # We could fail, but it's cleaner to just create one
        snapshot_manual_create.run()
        return latest_snapshot_id()
    id_, time = result
    return id_
