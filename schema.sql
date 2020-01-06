create table if not exists snapshots
( id integer primary key autoincrement
, time timestamp not null
);

create table if not exists currencies
( symbol varchar primary key
, name varchar not null
, active boolean not null default true
, fetcher varchar
);

create table if not exists currency_value
( symbol varchar not null references currencies(symbol)
, snapshot int not null references snapshots(id)
, value numeric not null
);

create unique index idx_currency_value_id_snapshot
on currency_value (symbol, snapshot);

create table if not exists accounts
( id integer primary key
, name varchar not null
, currency varchar not null references currencies(symbol)
, active boolean not null default true
, fetcher varchar
, fetcher_param varchar
);

create unique index idx_accounts_name
on accounts (name);

create table if not exists account_value
( id int not null references accounts(id)
, snapshot int not null references snapshots(id)
, value numeric not null
);

create unique index idx_account_value_id_snapshot
on account_value (id, snapshot);

create table if not exists categories
( id integer primary key
, name varchar not null
, parent integer references categories(id)
, default_amortization varchar not null default 'point'
);

create table if not exists transactions
( id integer primary key autoincrement
, account_id integer references accounts(id)
, day date not null
, amount numeric not null
, description varchar not null
, amortization varchar not null default 'point'
, category_id integer references categories(id)
);

create unique index idx_transactions_id
on transactions (id);

create view if not exists vw_transactions as
select t.id, t.day, t.amount, t.description, a.name as account, c.name as category
from transactions t
join accounts a on t.account_id = a.id
join categories c on t.category_id = c.id;
