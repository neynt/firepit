import db
import lib
import tabtab

CATEGORY = 'debug'

def run():
    """Lists currencies."""
    result = db.query_to_dataframe('''
    select c.symbol, c.name, c.active, cv.value
    from currencies c
    left join currency_value cv on c.symbol = cv.symbol
    left join currency_value cv2 on (c.symbol = cv2.symbol and cv.snapshot < cv2.snapshot)
    where cv2.snapshot is null
      and c.active = true
    ''')
    tabtab.format_dataframe(result)
