import db
import lib
import config
import modules

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

@lib.command()
def test_fetcher(name):
    global driver
    driver = config.make_webdriver()
    print(modules.FETCHERS[name].fetch(driver))
