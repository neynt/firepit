import db
from lib import latest_snapshot_id

CATEGORY = 'tracking'

def run(account_id, value):
    """Sets the value of the account for the latest snapshot."""
    snapshot_id = latest_snapshot_id()
    db.c.execute('''
    insert into account_value (id, snapshot, value)
    values (?, ?, ?)
    on conflict (id, snapshot)
    do update set value=?
    ''', (account_id, snapshot_id, value, value))
