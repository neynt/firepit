import db

CATEGORY = 'setup'

def run(name, currency):
    """Creates a new account."""
    db.c.execute('''
    insert into accounts (name, currency) values (?, ?)
    ''', (name, currency))
