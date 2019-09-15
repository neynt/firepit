from datetime import datetime, timezone

import db

CATEGORY = 'debug'

def run():
    db.execute('''
    insert into snapshots (time) values (?)
    ''', (datetime.now(timezone.utc),))
