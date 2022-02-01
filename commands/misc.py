import db
import lib

@lib.command()
def sql(query):
    """Runs a raw SQL query."""
    return db.query_to_dataframe(query)

@lib.command()
def mod(table, id_, prop_name, value):
    """Modifies a value in the database."""
    db.execute(f'''
    update {table}
    set {prop_name}=?
    where id=?
    ''', (value, id_))
