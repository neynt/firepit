URL = 'https://secure01a.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/index'

def fetch(driver, username, password):
    driver.get()
    driver.implicitly_wait(10)
    driver.switch_to.frame(0)
    driver.find_element_by_id('userId-input-field').send_keys(username)
    driver.find_element_by_id('password-input-field').send_keys(password)
    driver.find_element_by_id('signin-button').click()

    return []
