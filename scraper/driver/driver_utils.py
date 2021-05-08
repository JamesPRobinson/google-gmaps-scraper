import re
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException


ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

def click_element_by_xpath(driver, xpath, wait_val):
    wait = WebDriverWait(driver, wait_val, ignored_exceptions=ignored_exceptions)
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    driver.find_element_by_xpath(xpath).click()


def click_element_by_id(driver, element_id, wait_val):
    try:
        wait = WebDriverWait(driver, wait_val, ignored_exceptions=ignored_exceptions)
        wait.until(EC.presence_of_element_located((By.ID, element_id)))
        wait.until(EC.element_to_be_clickable((By.ID, element_id)))
        driver.find_element_by_id(element_id).click()
    except:
        pass

def check_google_consent(driver):
    # active the iframe and click the agree button
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe")))
    click_element_by_xpath(driver, '//*[@id="introAgreeButton"]/span/span', 10)
    #driver.execute_script("arguments[0].click();", agree)
    # back to the main page
    driver.switch_to_default_content()

def find_elements_by_xpath(driver, xpath, wait_val):
    try:
        wait = WebDriverWait(driver, wait_val, ignored_exceptions=ignored_exceptions)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        return driver.find_elements_by_xpath(xpath)
    except TimeoutException:
        return []


def find_element_by_xpath(driver, wait_val, xpath):
    wait = WebDriverWait(driver, wait_val, ignored_exceptions=ignored_exceptions)
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    return driver.find_element_by_xpath(xpath)

def solve_captcha(driver):
    API_KEY = 'c21d36ab4fca3fbc17a613b28901dad4'  # Your 2captcha API KEY
    url = driver.find_element_by_xpath("//iframe[contains(@src, 'www.google.com/recaptcha/api2')]") \
        .get_attribute("src")

    site_key = re.findall(r'k=(.*?)&', url)[0]

    s = requests.Session()

    captcha_id = s.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(
        API_KEY, site_key, url)).text.split('|')[1]
    recaptcha_answer = s.get(
        "http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text

    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        sleep(5)
        recaptcha_answer = s.get(
            "http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
    recaptcha_answer = recaptcha_answer.split('|')[1]

    driver.execute_script(f"___grecaptcha_cfg.clients[0].R.W.callback('{recaptcha_answer}')")