import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup

LINKEDIN_URL = "https://www.linkedin.com/"


class LinkedInScraper:
    def __init__(self, username, password, URLs):
        # constructing Chrome browser, if the devise doesn't have chrome, it needs to be installed
        self.browser = webdriver.Chrome()
        self.URLs = URLs
        self.__login(username, password)
        self.soup = None

    def __login(self, username, password):
        self.browser.get(LINKEDIN_URL)
        # login using LinkedIn username and password
        user_name = self.browser.find_element(By.ID, 'session_key')
        user_name.send_keys(username)
        sleep(0.5)

        session_pw = self.browser.find_element(By.ID, 'session_password')
        session_pw.send_keys(password)
        sleep(0.5)

        sign_in = self.browser.find_element(By.XPATH, '//*[@type="submit"]')
        sign_in.click()
        sleep(2)

    def __go_to_profile(self, URL):
        self.browser.get(URL)

        start = time.time()

        # will be used in the while loop
        initialScroll = 0
        finalScroll = 1000

        while True:
            self.browser.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
            # this command scrolls the window starting from
            # the pixel value stored in the initialScroll
            # variable to the pixel value stored at the
            # finalScroll variable
            initialScroll = finalScroll
            finalScroll += 1000

            # we will stop the script for 3 seconds so that
            # the data can load
            time.sleep(0.5)
            # You can change it as per your needs and internet speed

            end = time.time()

            # We will scroll for 20 seconds.
            # You can change it as per your needs and internet speed
            if round(end - start) > 5:
                break

        src = self.browser.page_source
        self.soup = BeautifulSoup(src, 'html.parser')

    def get_contact(self):
        self.browser.execute_script(
            "(function(){try{for(i in document.getElementsByTagName('a')){let el = document.getElementsByTagName("
            "'a')[i]; "
            "if(el.innerHTML.includes('Contact info')){el.click();}}}catch(e){}})()")

        # Wait 5 seconds for the page to load
        time.sleep(2)

        # Scrape the email address from the 'Contact info' popup
        email = self.browser.execute_script(
            "return (function(){try{for (i in document.getElementsByClassName('pv-contact-info__contact-type')){ let "
            "el = "
            "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
            "'ci-email')){ "
            "return el.children[2].children[0].innerText; } }} catch(e){return '';}})()")
        phone = self.browser.execute_script(
            "return (function(){try{for (i in document.getElementsByClassName('pv-contact-info__contact-type')){ let "
            "el = "
            "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
            "'ci-phone')){ "
            "return el.children[2].children[0].innerText; } }} catch(e){return '';}})()")
        return email, phone

    def get_intro(self, URL):
        '''
        getting the intro from the profile of a specific user
        :param URL:
            the URL of the user's profile
        :return:
        '''

        self.__go_to_profile(URL)
        intro1 = self.soup.find('div', {'class': 'pv-text-details__left-panel'})

        name = intro1.find('h1').get_text().strip()
        pronoun = intro1.find('span').get_text().strip()
        headline = intro1.find('div', {'class': 'text-body-medium break-words'}).get_text().strip()

        intro2 = self.soup.find('div', {'class': 'pv-text-details__left-panel mt2'})
        location = intro2.find('span').get_text().strip()

        return name, pronoun, headline, location
