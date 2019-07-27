# Super simple database schema and migration script.
# Add a column, and any existing rows will have it set to its default value.
# Remove a column, and the data will disappear.
# Change a column, and... you'll have to update it manually.

from collections import defaultdict
import re
import os
import sys
import sqlite3

def main():
  conn = sqlite3.connect('data.sqlite')

  schema = open('schema.sql').read()
  statements = map(str.strip, re.split(r';\n', schema))
  kinds = [
    'drop table',
    'create table',
    'index',
  ]

  statements_of_kind = defaultdict(list)
  for statement in statements:
    if not statement: continue
    for kind in kinds:
      if kind in statement:
        statements_of_kind[kind].append(statement)
        break
    else:
      print("Error: I don't know what this means. Stopping just in case.")
      print(statement)
      return

  c = conn.cursor()

  creates = []
  for statement in statements_of_kind['create table']:
    table_name = re.search(r'create table if not exists ([a-z_]+)', statement, re.DOTALL)[1]
    table_name_new = table_name + '_new'
    creates.append((table_name, table_name_new, statement))

  # Create dummy tables.
  for table_name, table_name_new, statement in creates:
    c.execute(statement)

  print('# Creating new tables and porting over data.')
  for table_name, table_name_new, statement in creates:
    print(f'## {table_name}')
    statement_new = re.sub(table_name, table_name_new, statement)
    c.execute(f'''
      drop table if exists {table_name_new}
    ''')
    c.execute(statement_new)
    c.execute(f'''
      pragma table_info({table_name})
    ''')
    old_columns = set(r[1] for r in c.fetchall())
    c.execute(f'''
      pragma table_info({table_name_new})
    ''')
    new_columns = set(r[1] for r in c.fetchall())
    shared_columns = list(old_columns & new_columns)
    added_columns = list(new_columns - old_columns)
    removed_columns = list(old_columns - new_columns)
    if added_columns:
      print(f'Columns added: {added_columns}')
    if removed_columns:
      print(f'Columns removed: {removed_columns}')
    ported_columns = ', '.join(shared_columns)
    c.execute(f'''
      INSERT INTO {table_name_new} ({ported_columns})
      SELECT {ported_columns} FROM {table_name};
    ''')

  # Delete original tables and rename new ones.
  print('# Replacing original tables.')
  for table_name, table_name_new, statement in creates:
    c.executescript(f'''
      drop table if exists {table_name};
      alter table {table_name_new} rename to {table_name};
    ''')

  print(f"# Creating {len(statements_of_kind['index'])} indexes.")
  for statement in statements_of_kind['index']:
    c.execute(statement)

  print('# Done')
  print('Committing.')
  conn.commit()

if __name__ == '__main__':
  main()
