import sqlite3
import pandas as pd

conn = sqlite3.connect('data.sqlite')
c = conn.cursor()

c.execute('pragma foreign_keys = on;')
conn.commit()

def query_to_dataframe(*args):
    c.execute(*args)
    data = c.fetchall()
    result = pd.DataFrame(data, columns=[desc[0] for desc in c.description])
    return result

def query(*args):
    c.execute(*args)
    return c.fetchall()

def execute(*args):
    c.execute(*args)
