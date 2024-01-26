from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

class HomeTest(LiveServerTestCase):

    def setUp(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

        self.selenium = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=chrome_options
        )
        self.selenium.implicitly_wait(10)

    def tearDown(self):
        self.selenium.quit()

    def test_home_text(self):
        self.selenium.get(f'{self.live_server_url}/')
        header_text = self.selenium.find_element(By.TAG_NAME, "h1").text
        self.assertEqual(header_text, "Home")
