from commands.snapshot import latest_snapshot_id

from prompt_toolkit import prompt

import db
import lib
import tabtab

@lib.command()
def accounts():
    """Lists accounts."""
    return db.query_to_dataframe('''
    select * from accounts order by name
    ''')

@lib.command()
def active_accounts():
    """Lists active accounts."""
    return db.query_to_dataframe('''
    select * from accounts order by name
    ''')

def prompt_account():
    accts = active_accounts()
    acct_names = accts.name.to_list()
    name = lib.prompt_list(acct_names, 'account')
    return int(accts[accts.name == name].id)

@lib.command()
def account_values():
    return db.query_to_dataframe('''
    select a.name, av.value, a.currency as curr
    from accounts a
    left join account_value av on av.id = a.id
    left join account_value av2 on (av2.id = av.id and av.snapshot < av2.snapshot)
    where av2.snapshot is null
      and av.value != 0
      and a.active = true
    ''', ())

@lib.command(category='setup')
def account_new(name, currency):
    """Creates a new account."""
    db.execute('''
    insert into accounts (name, currency) values (?, ?)
    ''', (name, currency))

@lib.command()
def account_record(account_id, value):
    """Sets the value of the account for the latest snapshot."""
    snapshot_id = latest_snapshot_id()
    db.execute('''
    insert into account_value (id, snapshot, value)
    values (?, ?, ?)
    on conflict (id, snapshot)
    do update set value=?
    ''', (account_id, snapshot_id, value, value))

@lib.command(category='setup')
def account_del():
    """Deletes an account."""
    accts = db.query_to_dataframe('''
    select id, name, currency
    from accounts
    ''')
    tabtab.print_dataframe(accts)
    id_ = lib.prompt('Delete which id? ')
    db.execute('''
    delete from accounts
    where id = ?
    ''', (id_,))

@lib.command()
def account_mod(account_id, prop_name, value):
    """Modifies a property of an account."""
    db.c.execute(f'''
    update accounts
    set {prop_name}=?
    where id=?
    ''', (value, account_id))

@lib.command(category='setup')
def account_set_fetcher(account_id, fetcher, fetcher_param):
    """Sets the fetcher for an account."""
    account_mod(account_id, 'fetcher', fetcher)
    account_mod(account_id, 'fetcher_param', fetcher_param)

@lib.command()
def account_history():
    """Shows history of an account over time."""
    result = db.query_to_dataframe('''
    select s.time, av.value, a.name, a.currency
    from accounts a
    left join account_value av on av.id = a.id
    left join snapshots s on av.snapshot = s.id
    ''', ())
    tabtab.print_dataframe(result)
