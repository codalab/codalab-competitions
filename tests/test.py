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
        temp_worksheet_name = 'test-codalab-' + str(random.randint(0, 1000000))
        temp_worksheet_title =  'The really long testing title for testing the automated testing of worksheets'
        temp_worksheet_uuid = self.run_command([cl, 'new', temp_worksheet_name])
        temp_file_name = 'cl-web-interface-testing.txt'
        temp_worksheet_paragraph_content = "For running automated testing on the cli " * 10
        self.run_command([cl, 'work', temp_worksheet_uuid])
        self.run_command([cl, 'wedit', '-t', temp_worksheet_title])
        self.run_command([cl, 'add',  '-m', temp_worksheet_paragraph_content])
        self.run_command(['touch', temp_file_name])
        temp_file_uuid = self.run_command([cl, 'upload', 'dataset', temp_file_name])

        # click the worksheet button on the top right of the main page
        self.browser.find_element_by_xpath("html/body/nav/div/div[2]/ul/li[1]/a").click()

        # find the worksheet that was just created
        self.browser.implicitly_wait(4)
        self.browser.get(self.browser.find_element_by_link_text(temp_worksheet_name).get_attribute('href'))

        # wait for a sec to make sure that the AJAX calls have been completed.
        # TODO: find a better and more selenium way to do it.
        import time
        time.sleep(1)

        # Make sure that there is no error displayed on the page
        self.assertNotIn('ERROR', self.browser.page_source)

        # check worksheet layout
        self.worksheetLayoutCheckHelper(temp_worksheet_name, temp_worksheet_uuid, temp_worksheet_title)

        # check worksheet sidepanel
        self.worksheetSidePanelCheckHelper(temp_worksheet_name, temp_worksheet_uuid, temp_file_name)

        # check worksheet content
        self.worksheetContentCheckHelper(temp_file_name, temp_file_uuid, temp_worksheet_paragraph_content)

        # delete the temp-worksheet
        self.run_command([cl, 'wrm', '--force', temp_worksheet_name])

        self.run_command(['rm', temp_file_name])

    def worksheetContentCheckHelper(self, temp_file_name, temp_worksheet_uuid, temp_worksheet_paragraph_content):
        # test paragraph content inserted at top of temp_worksheet
        self.assertIn(temp_worksheet_paragraph_content, self.browser.page_source)
        # check table in worksheet
        table_content = ['uuid','name', temp_file_name, 'description', 'bundle_type', 'dataset', 'created', 'dependencies', 'command', 'MISSING', 'data_size', '0','state', 'ready']
        for item in table_content:
            self.assertIn(item, self.browser.page_source)

    def worksheetLayoutCheckHelper(self, temp_worksheet_name, temp_worksheet_uuid, temp_worksheet_title):
        # check worksheet information
        for item in ['name:', 'uuid:', 'owner:', 'permissions:', "Keyboard Shortcuts", 'view', 'source', temp_worksheet_name, temp_worksheet_uuid, temp_worksheet_title]:
            self.assertIn(item, self.browser.page_source)

    def worksheetSidePanelCheckHelper(self, temp_worksheet_name, temp_worksheet_uuid, temp_file_name):
        for item in ['name', 'uuid', 'owner', 'permissions', 'type', temp_worksheet_name, temp_worksheet_uuid]:
            self.assertIn(item, self.browser.find_element_by_class_name('ws-panel').text)

if __name__ == '__main__':
    unittest.main(verbosity=2)
