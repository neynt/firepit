from selenium import webdriver

browser_cmd = 'firefox'

def make_webdriver():
    return webdriver.Firefox()

fetcher_credentials = {
    'capital_one': {
        'username': '',
        'password': '',
    },
}
