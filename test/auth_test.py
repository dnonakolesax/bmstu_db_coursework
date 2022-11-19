from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=options)

driver.get('localhost:5001')

driver.find_element(By.XPATH, 'safgaafs')

driver.close()

print('done')
