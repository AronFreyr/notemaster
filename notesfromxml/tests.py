import os

from django.test import TestCase

from selenium import webdriver


class SeleniumTests(TestCase):

    def test_selenium(self):

        chromedriver = r'C:/Users/default.default-PC/Downloads/chromedriver.exe'
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        driver.get("http://www.python.org")
        assert 'Python' in driver.title
        driver.quit()
