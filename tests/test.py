import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class CodalabTestCase(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.addCleanup(self.browser.quit)
        self.base_url = "http://localhost:8000/"

    def testPageTitle(self):
        self.browser.get(self.base_url)
        self.assertIn('CodaLab - Home', self.browser.title)

    def testWorksheetCompetionbuttons(self):
        self.browser.get(self.base_url)
        experiment_btn = self.browser.find_element_by_link_text("Create an Experiment!")
        self.assertIsNotNone(experiment_btn, msg=None)
        challenge_btn = self.browser.find_element_by_link_text("Join a challenge!")
        self.assertIsNotNone(challenge_btn, msg=None)
        

if __name__ == '__main__':
    unittest.main(verbosity=2)