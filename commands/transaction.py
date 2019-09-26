import db
import lib

@lib.command()
def transactions():
    return db.query_to_dataframe('''
    select id, account_id, category_id, day, amount, description, amortization
    from transactions
    order by day
    ''')

@lib.command()
def transactions_between(time_start, time_end):
    return db.query_to_dataframe('''
    select id, account_id, category_id, day, amount, description, amortization
    from transactions
    where day >= ? and day <= ?
    order by day
    ''', (time_start, time_end))

@lib.command()
def transaction_new(account_id, day, description, amount, category_id):
    db.execute('''
    insert into transactions (account_id, day, amount, description, category_id)
    values (?, ?, ?, ?, ?)
    ''', (account_id, day, amount, description, category_id))

@lib.prompter('description')
def prompt_transaction_description(*_args):
    descs = set(transactions().description)
    return lib.prompt_list_nonstrict(descs)

@lib.command()
def transaction_del(transaction_id):
    db.execute('''
    delete from transactions where id = ?
    ''', (transaction_id,))

@lib.command()
def transaction_loop(account_id):
    try:
        while True:
            ts = transactions()
            day = lib.PROMPTERS['day']('day: ')
            description = lib.PROMPTERS['description']('description: ')
            default_category = ts[ts.description == description].category_id
            # TODO: make this work
            print(default_category)
            lib.call_via_prompts(transaction_new, account_id, day, description)
    except KeyboardInterrupt:
        pass
