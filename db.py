import sqlite3

conn = sqlite3.connect('data.sqlite')

c = conn.cursor()
c.execute('pragma foreign_keys = on;')
conn.commit()
