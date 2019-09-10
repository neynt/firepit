import db
import lib

CATEGORY = 'debug'

def run():
    """Lists accounts."""
    db.c.execute('''
    select * from accounts order by name
    ''')
    lib.print_cursor(db.c)
