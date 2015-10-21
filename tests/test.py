import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

class CodalabTestCase(unittest.TestCase):

    def setUp(self):
        print "blah"
        self.browser = webdriver.Firefox()
        self.addCleanup(self.browser.quit)
        self.base_url = "http://localhost:8000/"

    def testBaseURL(self):
        self.browser.get(self.base_url)
        self.browser.maximize_window()
        self.assertIn('CodaLab - Home', self.browser.title)
        for i, item in enumerate(['Worksheets', 'Competitions', 'Help']):
            self.assertEqual(
                item,
                self.browser.find_element_by_xpath("html/body/nav/div/div[2]/ul/li[" + str(i+1) + "]/a").get_attribute('innerHTML')
            )
        for i, item in enumerate(['Create an Experiment!', 'Join a challenge!']):
            self.assertEqual(
                item,
                self.browser.find_element_by_xpath("html/body/div[2]/div/div/div[" + str(i+1) + "]/div/div/a").get_attribute('innerHTML')
            )
        
        assert "Run reproducible experiments and created executable papers using worksheets" in self.browser.page_source
        assert "Enter the existing competition to solve challenging data problems, or host your own." in self.browser.page_source
    
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