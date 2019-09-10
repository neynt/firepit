import db
from lib import latest_snapshot_id

CATEGORY = 'setup'

def run(symbol, value):
    """Sets the value of the account for the latest snapshot."""
    snapshot_id = latest_snapshot_id()
    db.c.execute('''
    insert into currency_value (symbol, snapshot, value)
    values (?, ?, ?)
    on conflict (symbol, snapshot)
    do update set value=?
    ''', (symbol, snapshot_id, value, value))
