import db
import lib
import tabtab

@lib.command()
def transactions():
    return db.query_to_dataframe('''
    select id, account_id, category, day, amount, description, amortization
    from transactions
    order by day
    ''')

@lib.command()
def transactions_between(min_date, max_date):
    return db.query_to_dataframe('''
    select id, account_id, category, day, amount, description, amortization
    from transactions
    where day >= ? and day <= ?
    order by day
    ''', (min_date, max_date))

@lib.command()
def transactions_for_account(account_id):
    return db.query_to_dataframe('''
    select id, account_id, category, day, amount, description, amortization
    from transactions
    where account_id = ?
    order by day
    ''', (account_id,))

@lib.command()
def transaction_new(account_id, day, description, amount):
    db.execute('''
    insert into transactions (account_id, day, amount, description)
    values (?, ?, ?, ?)
    ''', (account_id, day, amount, description))

@lib.prompter('description')
def prompt_transaction_description(*args):
    descs = set(transactions().description)
    return lib.prompt_list_nonstrict(descs, *args)

@lib.command()
def transaction_del(transaction_id):
    db.execute('''
    delete from transactions where id = ?
    ''', (transaction_id,))

@lib.command()
def transaction_loop(account_id):
    # First print out previous 3 transactions
    result = db.query_to_dataframe('''
    select day, amount, description
    from transactions
    where account_id = ?
    order by day desc
    limit 3
    ''', (account_id,))
    if result.empty:
        print('No previous transactions for this account.')
    else:
        print('Last transactions recorded:')
        tabtab.print_dataframe(result)
    try:
        print('Enter day; desc; amt')
        while True:
            day, desc, amt = lib.prompt_day_desc_price('> ')
            lib.call_via_prompts(transaction_new, account_id, day, desc, amt)
    except KeyboardInterrupt:
        pass
