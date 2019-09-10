import db
from commands import currency_list

CATEGORY = 'setup'

def run(symbol):
    """Deletes a currency from existence."""
    db.c.execute('''
    delete from currencies
    where symbol = ?
    ''', (symbol,))
    currency_list.run()
