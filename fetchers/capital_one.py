from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

def fetch(username, password):
  driver = webdriver.Firefox()
  driver.get("https://verified.capitalone.com/sic-ui/")
  driver.implicitly_wait(10)
  driver.find_element_by_id("username").send_keys(username)
  driver.find_element_by_id("password").send_keys(password)
  driver.find_element_by_id("id-signin-submit").click()
  element = driver.find_element_by_id("id-signin-submit")
  actions = ActionChains(driver)
  actions.move_to_element(element).perform()

  accounts = driver.find_elements_by_css_selector('account-message')
  account_data = {}
  for account in accounts:
    dollar = account.find_element_by_css_selector('span.dollar').text
    cents = account.find_element_by_css_selector('span.cents').text
    accnumtrail = account.find_element_by_css_selector('span.accnumbertrail').text
    title = account.find_element_by_css_selector('p.title')
    driver.implicitly_wait(0)
    image = title.find_elements_by_css_selector('img')
    print(image)
    driver.implicitly_wait(10)
    if image:
      print(image[0])
      global I
      I = image[0]
      product_name = image[0].get_attribute('product-name')
    else:
      product_name = title.find_element_by_css_selector('h2.headerTruncateLarge').text
    amount = float(f'{dollar}.{cents}'.replace(',', ''))
    account_data[f'{product_name} {accnumtrail}'] = amount

  return account_data
