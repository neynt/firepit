create table if not exists snapshots
( id integer primary key
, time datetime not null
);

create table if not exists currencies
( symbol varchar primary key not null
, name varchar not null
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
, url varchar
);

create table if not exists account_value
( id int references accounts(id)
, snapshot int not null references snapshots(id)
, value numeric not null
);

create unique index idx_account_value_id_snapshot
on account_value (id, snapshot);
