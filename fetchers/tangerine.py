url = 'https://www.tangerine.ca/app/'

def fetch(driver, username, pin):
  driver.get(url)
  driver.implicitly_wait(10)
  driver.find_element_by_id('login_clientId').click()
  driver.find_element_by_id('login_clientId').send_keys(username)
  driver.find_element_by_css_selector('#login_logMeIn > .ng-binding').click()
  driver.find_element_by_id('login_pin').send_keys(pin)
  driver.find_element_by_id('login_signIn').click()

  return []
