import db
from commands import currency_list

CATEGORY = 'setup'

def run(symbol, name):
    """Declares a new currency."""
    db.c.execute('''
    insert into currencies (symbol, name)
    values (?, ?)
    ''', (symbol, name))
    currency_list.run()
