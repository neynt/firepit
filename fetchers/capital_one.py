import config

URL = 'https://verified.capitalone.com/sic-ui/'

def fetch(driver):
    username, password = config.FETCHER_CREDENTIALS['capital_one']
    driver.get(URL)
    driver.implicitly_wait(10)
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_id('id-signin-submit').click()

    accounts = driver.find_elements_by_css_selector('account-message')
    account_data = {}
    for account in accounts:
        dollar = account.find_element_by_css_selector('span.dollar').text
        cents = account.find_element_by_css_selector('span.cents').text
        accnumtrail = account.find_element_by_css_selector('span.accnumbertrail').text
        title = account.find_element_by_css_selector('p.title')
        driver.implicitly_wait(0)
        image = title.find_elements_by_css_selector('img')
        driver.implicitly_wait(10)
        if image:
            product_name = image[0].get_attribute('product-name')
        else:
            product_name = title.find_element_by_css_selector('h2.headerTruncateLarge').text
        amount = float(f'{dollar}.{cents}'.replace(',', ''))
        account_data[f'{product_name} {accnumtrail}'] = amount

    return account_data
