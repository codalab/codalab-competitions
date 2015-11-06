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
import time

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

        # Make sure that there is no error displayed on the page
        self.assertNotIn('ERROR', self.browser.page_source)
        # check title
        self.assertIn('CodaLab - Home', self.browser.title)

        for item in ['Worksheets', 'Competitions', 'Help', 'Example Worksheets', 'Latest Competitions']:
            self.assertIn(item, self.browser.page_source)

    def testWorksheetContent(self):
        cl = 'cl'
        self.browser.get(self.base_url)
        self.browser.maximize_window()
        
        # create a temp worksheet for testing
        selenium_test_worksheet_name = 'Codalab-UI-selenium-testing'
        temp_file_name = 'cl-web-interface-testing.txt'
        temp_worksheet_name = 'test-codalab-' + str(random.randint(0, 1000000))
        temp_worksheet_title =  'The really long testing title for testing the automated testing of worksheets'
        temp_worksheet_paragraph_content = "For running automated testing on the cli " * 7
        self.created_worksheets = []
        try:
            selenium_test_worksheet_uuid = self.run_command([cl, 'new', selenium_test_worksheet_name])
            self.created_worksheets.append(selenium_test_worksheet_name)
            self.run_command(['touch', temp_file_name])
            self.run_command([cl, 'work', selenium_test_worksheet_name])
            # click the worksheet button on the top right of the main page
            self.browser.find_element_by_link_text("Worksheets").click()

            # find the worksheet that was just created
            self.browser.implicitly_wait(4)
            self.browser.get(self.browser.find_element_by_link_text(selenium_test_worksheet_name).get_attribute('href'))

            # wait for a sec to make sure that the AJAX calls have been completed.
            # TODO: find a better and more selenium way to do it.
            self.waitToLoad()
            # Make sure that there is no error displayed on the page
            self.assertNotIn('ERROR', self.browser.page_source)

            self.worksheetActionBarHelper(temp_worksheet_name, temp_worksheet_title, temp_worksheet_paragraph_content, temp_file_name)
            # check worksheet layout
            self.worksheetLayoutCheckHelper(temp_worksheet_name, temp_worksheet_title)

            # check worksheet sidepanel
            self.worksheetSidePanelCheckHelper(temp_worksheet_name, temp_file_name)

            # check worksheet content
            self.worksheetContentCheckHelper(temp_file_name, temp_worksheet_paragraph_content)

            # delete the temp-worksheet
            action_bar = self.focusActionBar()
            self.executeActionBarCommands(action_bar, 'cl wrm --force '+selenium_test_worksheet_name)
            self.executeActionBarCommands(action_bar, 'cl wrm --force '+temp_worksheet_name)
            # self.run_command([cl, 'wrm', '--force', selenium_test_worksheet_name])
        except:
            print "Error occured while testing. Removing temprary worksheets created for testing..."
            for worksheet in self.created_worksheets:
                self.run_command([cl, 'wrm', '--force', worksheet])

        self.run_command(['rm', temp_file_name])


    def waitToLoad(self):
        time.sleep(1)

    def executeActionBarCommands(self, action_bar, command):
        action_bar.send_keys(command)
        action_bar.send_keys(Keys.ENTER)
        self.waitToLoad()

    def focusActionBar(self):
        action_bar = self.browser.find_element_by_id("ws_search")
        action_bar.send_keys('c')
        return action_bar

    def refreshWorksheet(self):
        worksheet = self.browser.find_element_by_id("worksheet")
        worksheet.click()
        worksheet.send_keys(Keys.SHIFT, 'r')

    def worksheetActionBarHelper(self, temp_worksheet_name, temp_worksheet_title, temp_worksheet_paragraph_content, temp_file_name):
        action_bar = self.focusActionBar()
        self.executeActionBarCommands(action_bar, 'cl new '+temp_worksheet_name)
        self.created_worksheets.append(temp_worksheet_name)
        action_bar = self.focusActionBar()
        self.executeActionBarCommands(action_bar, 'cl wedit -t "'+temp_worksheet_title+'"')
        self.executeActionBarCommands(action_bar, 'cl add -m "'+temp_worksheet_paragraph_content+'"')
        self.run_command(['cl', 'work', temp_worksheet_name])
        temp_file_uuid = self.run_command(['cl', 'upload', 'dataset', temp_file_name])
        self.refreshWorksheet()


    def worksheetContentCheckHelper(self, temp_file_name, temp_worksheet_paragraph_content):
        # test paragraph content inserted at top of temp_worksheet
        self.assertIn(temp_worksheet_paragraph_content, self.browser.page_source)
        # check table in worksheet
        table_content = ['uuid','name', temp_file_name, 'description', 'bundle_type', 'dataset', 'created', 'dependencies', 'command', 'data_size', '0','state', 'ready']
        for item in table_content:
            self.assertIn(item, self.browser.page_source)

    def worksheetLayoutCheckHelper(self, temp_worksheet_name, temp_worksheet_title):
        # check worksheet information
        for item in ['name:', 'uuid:', 'owner:', 'permissions:', "Keyboard Shortcuts", 'view', 'source', temp_worksheet_name, temp_worksheet_title]:
            self.assertIn(item, self.browser.page_source)

    def worksheetSidePanelCheckHelper(self, temp_worksheet_name, temp_file_name):
        for item in ['name', 'uuid', 'owner', 'permissions', 'type', temp_worksheet_name]:
            self.assertIn(item, self.browser.find_element_by_class_name('ws-panel').text)

if __name__ == '__main__':
    unittest.main(verbosity=2)
