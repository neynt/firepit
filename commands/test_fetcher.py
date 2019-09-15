import lib
import config
import modules

@lib.command()
def run(name):
    global driver
    driver = config.make_webdriver()
    print(modules.FETCHERS[name].fetch(driver, **config.FETCHER_CREDENTIALS[name]))
