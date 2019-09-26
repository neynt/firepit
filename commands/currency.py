from commands.snapshot import latest_snapshot_id

import db
import lib

@lib.command()
def currencies():
    """Lists currencies."""
    result = db.query_to_dataframe('''
    select c.symbol, c.name, c.active, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    left join currency_value cv2 on (c.symbol = cv2.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null
      and c.active = true
    ''')
    return result

@lib.command()
def currency_values(snapshot_id):
    return db.query_to_dataframe('''
    select c.symbol, c.name, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    where cv.snapshot = ?
    ''', (snapshot_id,))

@lib.command()
def hacky_latest_currency_values():
    """Super hacky way to get the latest currency values without a subquery."""
    return db.query_to_dataframe('''
    select c.symbol, c.name, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    left join currency_value cv2 on (c.symbol = cv2.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null
      and c.active = true
    ''').set_index('symbol')

@lib.command(category='setup')
def currency_new(symbol, name):
    """Declares a new currency."""
    db.execute('''
    insert into currencies (symbol, name)
    values (?, ?)
    ''', (symbol, name))
    return currencies()

@lib.command(category='setup')
def currency_del(symbol):
    """Deletes a currency from existence."""
    db.execute('''
    delete from currencies
    where symbol = ?
    ''', (symbol,))
    return currencies()

@lib.command()
def currency_record(symbol, value):
    """Sets the value of the account for the latest snapshot."""
    snapshot_id = latest_snapshot_id()
    db.execute('''
    insert into currency_value (symbol, snapshot, value)
    values (?, ?, ?)
    on conflict (symbol, snapshot)
    do update set value=?
    ''', (symbol, snapshot_id, value, value))
