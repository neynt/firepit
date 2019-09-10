import db
from lib import latest_snapshot_id, print_cursor

CATEGORY = 'tracking'

def run():
    """Shows history of an account over time."""
    db.c.execute('''
    select a.id, s.time, av.value, a.name, a.currency
    from accounts a
    left join account_value av on av.id = a.id
    left join snapshots s on av.snapshot = s.id
    ''', ())
    print_cursor(db.c)
