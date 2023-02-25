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

    def __go_to_page(self, URL):
        self.browser.get(URL)

        start = time.time()
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

            # stop the script for 0.5 seconds so that
            # the data can load
            time.sleep(0.5)
            # You can change it as per your needs and internet speed

            end = time.time()

            # We will scroll for 3 seconds.
            # You can change it as per your needs and internet speed
            if round(end - start) > 3:
                break

        src = self.browser.page_source
        self.soup = BeautifulSoup(src, 'html.parser')

    def get_contact(self, URL):
        '''
        getting the contact information of the user
        :param URL:
            the URL of the user's profile
        :return:
            email and phone number of the user(if provided)
            None if the info isn't provided
        '''
        self.__go_to_page(URL)
        self.browser.execute_script(
            "(function(){try{for(i in document.getElementsByTagName('a')){let el = document.getElementsByTagName("
            "'a')[i]; "
            "if(el.innerHTML.includes('Contact info')){el.click();}}}catch(e){}})()")

        # Wait 1 seconds for the page to load
        sleep(1)

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
            name, pronoun, headline, location of the user
            None if the info isn't provided
        '''

        self.__go_to_page(URL)
        intro1 = self.soup.find('div', {'class': 'pv-text-details__left-panel'})

        name = intro1.find('h1')
        if name:
            name = name.get_text().strip()

        pronoun = intro1.find('span')
        if pronoun:
            pronoun = pronoun.get_text().strip()

        headline = intro1.find('div', {'class': 'text-body-medium break-words'})
        if headline:
            headline = headline.get_text().strip()

        intro2 = self.soup.find('div', {'class': 'pv-text-details__left-panel mt2'})
        location = intro2.find('span')
        if location:
            location = location.get_text().strip()

        return name, pronoun, headline, location

    def get_experiences(self, URL):
        experiences = []
        self.__go_to_page(URL + "details/experience/")

        sleep(1)

        # getting all the li that is about experiences
        experiences_html = self.soup.findAll('li', {'class': 'pvs-list__paged-list-item artdeco-list__item '
                                                             'pvs-list__item--line-separated'})

        for experience_html in experiences_html:
            # if the user have had multiple experiences at one company, the format is different
            have_multi_exp = experience_html.findAll('a', {'class': 'optional-action-target-wrapper display-flex '
                                                               'flex-column full-width'})

            # if no multiple experiences
            if not have_multi_exp:

                title = experience_html.find('span', {'class': 'mr1 t-bold'}). \
                    find('span', {'aria-hidden': 'true'}).get_text()
                company = experience_html.find('span', {'class': 't-14 t-normal'}). \
                    find('span', {'aria-hidden': 'true'}).get_text()

                work_time = experience_html.find('span', {'class': 't-14 t-normal t-black--light'}).\
                    find('span', {'aria-hidden': 'true'}).get_text().strip()

                content_html = experience_html.find('div', {'class': 'display-flex align-items-center t-14 t-normal '
                                                                     't-black'})
                content = content_html.find('span', {'aria-hidden': 'true'}).get_text() \
                    if content_html else None

                experience = {
                    'Title': title,
                    'Company': company,
                    'Employ time': work_time,
                    'Work content': content
                }
                experiences.append(experience)

            else:
                company = experience_html.find('span', {'aria-hidden': 'true'}).get_text()
                roles = experience_html.findAll('li', {'class': 'pvs-list__paged-list-item  '})

                for role in roles:
                    title = role.find('span', {'class': 'mr1 hoverable-link-text t-bold'}). \
                        find('span', {'aria-hidden': 'true'}).get_text()
                    work_time = role.find('span', {'class': 't-14 t-normal t-black--light'}).\
                        find('span', {'aria-hidden': 'true'}).get_text()

                    content_html = role.find('div', {'class': 'display-flex'})
                    content = content_html.find('span', {'aria-hidden': 'true'}).get_text() \
                        if content_html else None
                    experience = {
                        'Title': title,
                        'Company': company,
                        'Employ time': work_time,
                        'Work content': content
                    }
                    experiences.append(experience)

        return experiences
