from commands.snapshot import latest_snapshot_id

import db
import lib

@lib.command()
def accounts():
    """Lists accounts."""
    return db.query_to_dataframe('''
    select * from accounts order by name
    ''')

@lib.prompter('account_id')
def prompt_account(*_args):
    accts = active_accounts()
    acct_names = accts.name.to_list()
    name = lib.prompt_list(acct_names, 'account: ')
    return int(accts[accts.name == name].id)

@lib.command()
def active_accounts():
    """Lists active accounts."""
    return db.query_to_dataframe('''
    select * from accounts
    where active
    order by name
    ''')

@lib.command()
def account_values(snapshot_id):
    return db.query_to_dataframe('''
    select a.id, a.name, av.value, a.currency as curr
    from accounts a
    left join account_value av on av.id = a.id
    where av.snapshot = ?
    ''', (snapshot_id,))

@lib.command()
def hacky_latest_account_values():
    """Super hacky way to get the latest account values without a subquery."""
    return db.query_to_dataframe('''
    select a.id, a.name, av.value, a.currency as curr
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
def account_record(account_id, snapshot_id, value):
    """Sets the value of the account for the latest snapshot."""
    db.execute('''
    insert into account_value (id, snapshot, value)
    values (?, ?, ?)
    on conflict (id, snapshot)
    do update set value=?
    ''', (account_id, snapshot_id, value, value))

@lib.command(category='setup')
def account_del(account_id):
    """Deletes an account."""
    db.execute('''
    delete from accounts
    where id = ?
    ''', (account_id,))

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
    return db.query_to_dataframe('''
    select s.time, av.value, a.name, a.currency
    from accounts a
    left join account_value av on av.id = a.id
    left join snapshots s on av.snapshot = s.id
    ''', ())
