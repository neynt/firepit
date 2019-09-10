import config
import modules

CATEGORY = 'debug'

def run(name):
    global driver
    driver = config.make_webdriver()
    print(modules.FETCHERS[name].fetch(driver, **config.FETCHER_CREDENTIALS[name]))
