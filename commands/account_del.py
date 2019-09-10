import db
import tabtab

CATEGORY = 'setup'

def run():
    """Deletes an account."""
    c = db.c
    c.execute('''
    select id, name, currency
    from accounts
    ''')
    print(tabtab.format(c.fetchall(), headers=['Id', 'Name', 'Currency']))
    print('Delete which id?')
    id_ = input('> ')
    c.execute('''
    delete from accounts
    where id = ?
    ''', (id_,))

