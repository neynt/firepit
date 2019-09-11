# Firepit

~ it's personal finance with a pit ~

## Goals

- Keep track of your finances across all sorts of different accounts and
  currencies
- Automatically scrape transaction logs and account balances
- Structured sqlite database

## Fetchers

Ideally, these would automatically fetch your account balances by automating
your browser. In reality, this doesn't work very well because Selenium insists
on copying your browser profile (which can easily exceed 800MB these days) and
doesn't offer an option to use the profile in place -- and using a fresh
profile results in most banks complaining about you having never used this
device before.

So fetchers are on hold.

## TOOD

- Currency fetchers
- Autocompletion when it matters (fzf?)
- Transactions
- Selenium-based automatic fetcher
- Reconciling transactions
