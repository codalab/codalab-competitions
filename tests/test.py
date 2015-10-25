import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import random

class CodalabTestCase(unittest.TestCase):

    def run_command(self, args, expected_exit_code=0):
        try:
            output = subprocess.check_output(args)
            exitcode = 0
        except subprocess.CalledProcessError, e:
            output = e.output
            exitcode = e.returncode
        print '>> %s (exit code %s, expected %s)\n%s' % (args, exitcode, expected_exit_code, output)
        assert expected_exit_code == exitcode, 'Exit codes don\'t match'
        return output.rstrip()

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

    def testWorksheetContent(self):
        cl = 'cl'
        self.browser.get(self.base_url)
        
        # create a temp worksheet for testing
        temp_worksheet_name = 'test-codalab-' + str(random.randint(0, 1000000))
        temp_worksheet_uuid = self.run_command([cl, 'new', temp_worksheet_name])
        self.run_command([cl, 'work', temp_worksheet_uuid])

        # click the worksheet button on the top right of the main page
        self.browser.find_element_by_xpath("html/body/nav/div/div[2]/ul/li[1]/a").click()

        # find the worksheet that we just created
        self.browser.implicitly_wait(4)
        self.browser.get(self.browser.find_element_by_link_text(temp_worksheet_name).get_attribute('href'))

        # we need to wait for a sec to make sure that the AJAX calls have been completed.
        # TODO: find a better and more selenium way to do it.
        import time
        time.sleep(1)
        # check the main contents of worksheet
        self.mainWorksheetContentCheckHelper(temp_worksheet_name, temp_worksheet_uuid)

        # check the worksheet sidepanel
        self.worksheetSidePanelCheckHelper(temp_worksheet_name, temp_worksheet_uuid)

        # delete the temp-worksheet
        self.run_command([cl, 'wrm', '--force', temp_worksheet_name])

    def mainWorksheetContentCheckHelper(self, temp_worksheet_name, temp_worksheet_uuid):
        # check name
        self.assertEqual('name:',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[1]/b").get_attribute('innerHTML')
        )
        #check name value
        self.assertEqual(temp_worksheet_name,
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[1]/span[2]").get_attribute('innerHTML')
        )

        # check uuid
        self.assertEqual('uuid:',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[2]/b").get_attribute('innerHTML')
        )
        # check uuid value
        self.assertEqual(temp_worksheet_uuid,
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[2]/span[2]").get_attribute('innerHTML')
        )

        # check owner
        self.assertEqual('owner:',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[3]/b").get_attribute('innerHTML')
        )

        # check permissions
        self.assertEqual('permissions:',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[4]/b").get_attribute('innerHTML')
        )

        # check keyboard-shortcuts

        self.assertEqual(' Keyboard Shortcuts',
            self.browser.find_element_by_xpath('html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[2]/div/a/span').get_attribute('innerHTML')
        )

        self.assertEqual('View',
            self.browser.find_element_by_xpath('html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[2]/div/div/div/button[1]').get_attribute('innerHTML')
        )

        self.assertEqual('Edit source',
            self.browser.find_element_by_xpath('html/body/div[3]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[2]/div/div/div/button[2]').get_attribute('innerHTML')
        )

    def worksheetSidePanelCheckHelper(self, temp_worksheet_name, temp_worksheet_uuid):
        # SIDE PANEL TESTS

        # check name
        self.assertEqual('name',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[1]/div/table/tbody/tr[1]/th").get_attribute('innerHTML')
        )
        # check name value
        self.assertEqual(temp_worksheet_name,
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[1]/div/table/tbody/tr[1]/td").get_attribute('innerHTML')
        )

        # check uuid
        self.assertEqual('uuid',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[1]/div/table/tbody/tr[2]/th").get_attribute('innerHTML')
        )

        # check uuid value
        self.assertEqual(temp_worksheet_uuid,
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[1]/div/table/tbody/tr[2]/td").get_attribute('innerHTML')
        )


        # check owner
        self.assertEqual('owner',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[1]/div/table/tbody/tr[3]/th").get_attribute('innerHTML')
        )

        # check permissions
        self.assertEqual('permissions',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[1]/div/table/tbody/tr[4]/th").get_attribute('innerHTML')
        )

        # check table headings
        self.assertEqual('type',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[1]/div/div/table/thead/tr/th[1]").get_attribute('innerHTML')
        )

        self.assertEqual('name',
            self.browser.find_element_by_xpath("html/body/div[3]/div/div[2]/div[1]/div/div/table/thead/tr/th[2]").get_attribute('innerHTML')
        )

if __name__ == '__main__':
    unittest.main(verbosity=2)