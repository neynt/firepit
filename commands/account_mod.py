import db

CATEGORY = 'debug'

def run(account_id, prop_name, value):
    """Modifies a property of an account."""
    db.c.execute(f'''
    update accounts
    set {prop_name}=?
    where id=?
    ''', (value, account_id))
