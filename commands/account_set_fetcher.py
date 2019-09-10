from commands import account_mod

CATEGORY = 'setup'

def run(account_id, fetcher, fetcher_param):
    """Sets the fetcher for an account."""
    account_mod.run(account_id, 'fetcher', fetcher)
    account_mod.run(account_id, 'fetcher_param', fetcher_param)
