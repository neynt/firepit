import db
import lib
import tabtab

@lib.command()
def transaction_new(account_id, day, description, category_id):
    db.execute('''
    insert into transactions (account_id, day, description, category_id)
    values (?, ?, ?, ?)
    ''', (account_id, day, description, category_id))
