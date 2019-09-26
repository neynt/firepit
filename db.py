import sqlite3
import pandas as pd

sqlite3.register_adapter(bool, int)
sqlite3.register_converter("boolean", lambda v: bool(int(v)))

conn = sqlite3.connect('data.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

c.execute('pragma foreign_keys = on;')
conn.commit()

def begin():
    global c
    c = conn.cursor()

def commit():
    conn.commit()

def rollback():
    conn.rollback()

def query_to_dataframe(*args):
    c.execute(*args)
    data = c.fetchall()
    result = pd.DataFrame(data, columns=[desc[0] for desc in c.description])
    return result

def query(*args):
    c.execute(*args)
    return c.fetchall()

def query_one(*args):
    c.execute(*args)
    return c.fetchone()

def last_row_id():
    return c.lastrowid

def insert(*args):
    c.execute(*args)
    return c.lastrowid

def execute(*args):
    c.execute(*args)
