import os
from django.conf import settings
from django.utils.unittest.case import skip
from django.test import LiveServerTestCase

import selenium.webdriver.firefox.webdriver
import selenium.webdriver.chrome.webdriver
from selenium.webdriver.support.wait import WebDriverWait


selenium_can_start = lambda: getattr(settings, 'ENABLE_SELENIUM', True) and 'DISPLAY' in os.environ


class SkipSeleniumTestChecker(type):
    def __new__(mcs, name, bases, attrs):
        super_new = super(SkipSeleniumTestChecker, mcs).__new__
        if not selenium_can_start():
            for name, func in attrs.items():
                if callable(func) and name.startswith('test'):
                    attrs[name] = skip('Selenium disabled')(func)
        return type.__new__(mcs, name, bases, attrs)


class SeleniumTestCase(LiveServerTestCase):
    __metaclass__ = SkipSeleniumTestChecker
    driver = None

    @property
    def base_url(self):
        return self.live_server_url

    @classmethod
    def setUpClass(cls):
        if selenium_can_start():
            super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        if selenium_can_start():
            super(SeleniumTestCase, cls).tearDownClass()

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        if selenium_can_start():
            self.driver = self.driverClass()

    def tearDown(self):
        super(SeleniumTestCase, self).tearDown()
        if self.driver:
            self.driver.quit()

    def run(self, result=None):
        super(SeleniumTestCase, self).run(result)

    def go(self, url):
        self.driver.get('%s%s' % (self.live_server_url, url))

    def login(self, username='sax', password='123'):
        driver = self.driver
        driver.get(self.base_url + "/login/?next=/")
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys(username)
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys(password)
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        WebDriverWait(driver, 5).until(lambda driver: driver.find_element_by_id('welcome_header'))
        self.assertTrue("Welcome" in self.driver.find_element_by_id('welcome_header').text)

