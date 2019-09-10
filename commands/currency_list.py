import db
import lib

CATEGORY = 'reporting'

def run():
    """Lists currencies."""
    db.c.execute('''
    select c.symbol, c.name, c.active, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    left join currency_value cv2 on (c.symbol = cv2.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null
      and c.active = true
    ''')
    lib.print_cursor(db.c)
