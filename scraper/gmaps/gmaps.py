from collections import defaultdict
import queue
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
    StaleElementReferenceException, NoSuchElementException, 
    ElementClickInterceptedException
    )
from time import sleep
from ..driver import driver
from ..driver.driver_utils import check_google_consent, find_element_by_xpath, find_elements_by_xpath, click_element_by_xpath, solve_captcha
from .. import output

ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)


class GoogleMaps():
    def __init__(self,q=None, proxy=None):
        self.driver = None 
        self.locality = ''
        self.queue = q
        self.proxy = proxy
        self.query = ' '

 
    def parse_carousel(self, container):
        listings = []
        containers_xpath = "//div[contains(@class, 'has-image')]//div[contains(@class, 'body-content')]//div[contains(@class, 'action')]//div//div"
        try:
            click_element_by_xpath(self.driver, container, 20)
            wait = WebDriverWait(self.driver, 20, ignored_exceptions=ignored_exceptions)
            wait.until(ec.presence_of_all_elements_located((By.XPATH, containers_xpath)))
            listings = find_elements_by_xpath(self.driver, containers_xpath, 20)
            for listing in listings:
                record = defaultdict(lambda: '')
                record['city'] = self.locality
                record['query'] = self.query
                try:
                    record['name'] = listing.find_element(By.XPATH, "../../..//..").get_attribute('aria-label')
                except:
                    pass
                try:
                    record['service'] = listing.find_element(By.XPATH, "..//..//..//div[contains(@class, 'text')]//div[contains(@class, 'info')]").text
                except:
                    pass 
                try:
                    record['website'] = listing.get_attribute('data-tooltip').replace("\t", '').replace("\n", '').replace("\r", '').replace('"', '').strip()
                except:                      
                    pass
                self.queue.put(record, timeout=10)
            self.driver.back()
            sleep(5)
        except:
            self.driver.back()
        return listings


    def parse_listings(self, links):
        found_listing_xpath = "//h1[contains(@class, 'section-hero')]" # title loaded
        for link in links:
            try:             
                self.driver.get(link)
                wait = WebDriverWait(self.driver, 20, ignored_exceptions=ignored_exceptions)
                wait.until(ec.presence_of_all_elements_located((By.XPATH, found_listing_xpath)))
            except:
                pass
            record = defaultdict(lambda: '')
            record['city'] = self.locality
            record['query'] = self.query
            try:
                record['name'] = find_element_by_xpath(self.driver, 10, "//h1[contains(@class, 'section-hero-header-title')]//span[.!='']").text
            except:
                pass           
            try:
                record['website'] = find_element_by_xpath(self.driver, 10,"//button[contains(@aria-label, 'web:')]").get_attribute("aria-label").replace('Web site: ', '').replace('\t', '').replace('\n', '').replace('\r', '').replace('"', '').strip()
            except:
                pass       
            try:
                record['service'] = find_element_by_xpath(self.driver, 10, "//button[contains(@jsaction, 'category')]").text
                record['service'] =  record['GMAPS_Listing'].replace('\t', '').replace('\n', '').replace('\r', '').replace('"', '').strip()
            except:
                pass       
            try:
                record['phone_number'] = find_element_by_xpath(self.driver, 10,"//button[contains(@data-item-id, 'phone')]").text
            except:
                pass
            try:
                record['address'] = find_element_by_xpath(self.driver, 10,"//button[contains(@data-item-id, 'address')]").get_attribute("aria-label").replace('Indirizzo: ', '')
                record['address'] = record['address'].replace('\t', '').replace('\n', '').replace('\r', '').replace('"', '').strip()
            except:
                pass
            if record['website'] or record['phone_number']:
                self.queue.put(record, timeout=10)


    def scrape_queries(self, queries):
        for query in queries:
            self.locality = query[0]
            self.query = query[1] + ' ' + self.locality
            if not self.driver:
                self.driver = driver.get_driver(self.proxy)
            url = f"https://www.google.com/maps/search/{self.query}"
            try:
                self.driver.get(url)
            except:
                continue
            # Handling consent agreement pop-up...
            try:
                check_google_consent(self.driver)
            except:
                pass
            # Handle screen-wide variation...
            try:
                click_element_by_xpath(self.driver, "//button[contains(@aria-label, 'Acc')]", 15)
            except:
                pass
            # check for captcha
            try:
                find_element_by_xpath(self.driver, 10, "//iframe[contains(@src, 'www.google.com/recaptcha/api2')]")
            except:
                pass
            carousel, pages, records = True, 0, []
            while pages < 5:
                print(self.driver.current_url)
                pages += 1
                print('page:  ', pages)
                try:
                    # Wait for each listing page to load, check for alternative layout...
                    wait = WebDriverWait(self.driver, 20, ignored_exceptions=ignored_exceptions)
                    containers = "//a[contains(@class, 'place-result-container-place-link')]" 
                    try:                                            
                        wait.until(ec.element_to_be_clickable((By.XPATH, containers)))
                    except:
                        containers = "//div[contains(@class, 'result-container-click')]"
                        wait.until(ec.element_to_be_clickable((By.XPATH, containers)))          
                    if carousel:
                        res = self.parse_carousel(containers)               
                        if not res: # no carousels on page found
                            carousel = False
                    if not carousel:
                        records.extend([e.get_attribute('href') for e in find_elements_by_xpath(self.driver, containers, 30) if e.get_attribute('href')])
                    for i in range(pages):
                        next_page_xpath = "//button[contains(@id, 'pagination-button-next')]"
                        click_element_by_xpath(self.driver, next_page_xpath, 15)
                        sleep(5)
                except:
                    break
            if records:
                self.parse_listings(list(set(records)))