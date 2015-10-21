import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

class CodalabTestCase(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.addCleanup(self.browser.quit)
        self.base_url = "http://localhost:8000/"

    def testBaseURL(self):
        self.browser.get(self.base_url)
        self.browser.maximize_window()

        # check title
        self.assertIn('CodaLab - Home', self.browser.title)

        #check the list in the top right
        for i, item in [(1, 'Worksheets'), (2, 'Competitions'), (3, 'Help')]:
            self.assertEqual(
                item,
                self.browser.find_element_by_xpath("html/body/nav/div/div[2]/ul/li[" + str(i) + "]/a").get_attribute('innerHTML')
            )

        for i, item in [(1, 'Worksheets'), (2, 'Competitions')]:
            self.assertEqual(
                item,
                self.browser.find_element_by_xpath("html/body/div[2]/div/div/div[" + str(i) + "]/div/div/a").get_attribute('innerHTML')
            )

        assert "Run reproducible experiments and created executable papers using worksheets" in self.browser.page_source
        assert "Enter an existing competition to solve challenging data problems, or host your own." in self.browser.page_source
    
        for i, item in ([(3, 'Example Worksheets'), (4, 'Latest Competitions')]):
            self.assertEqual(
                item,
                self.browser.find_element_by_xpath("html/body/div[2]/div/div/div[" + str(i) + "]/h2").get_attribute('innerHTML')
            )

    def testWorksheet(self):
        self.browser.get(self.base_url)
        self.browser.find_element_by_xpath("html/body/nav/div/div[2]/ul/li[1]/a").click()
        self.assertEqual('Worksheets',
            self.browser.find_element_by_xpath("html/body/div[1]/div/h1").get_attribute('innerHTML')
        )
        
        
    # def testWorksheetCompetionbuttons(self):
    #     self.browser.get(self.base_url)
    #     experiment_btn = self.browser.find_element_by_link_text("Create an Experiment!")
    #     self.assertIsNotNone(experiment_btn, msg=None)
    #     challenge_btn = self.browser.find_element_by_link_text("Join a challenge!")
    #     self.assertIsNotNone(challenge_btn, msg=None)
        

if __name__ == '__main__':
    unittest.main(verbosity=2)