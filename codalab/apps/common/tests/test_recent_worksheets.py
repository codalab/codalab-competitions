import mock

from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

from ..utils import recent_worksheets


User = get_user_model()


class WorksheetHelperTests(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="organizer", password="pass")

	def test_recent_worksheets_non_logged_in_user(self):
		assert False

	@override_settings(BUNDLE_SERVICE_URL=None)
	def test_recent_worksheets_logged_in_user_empty_worksheet_list(self):
		import ipdb;ipdb.set_trace()
		#self.client.login(username='organizer', password='pass')
		with mock.patch('apps.common.utils.BundleService.worksheets') as worksheet_endpoint_mock:
			import ipdb;ipdb.set_trace()
			worksheet_endpoint_mock.return_value = ['test', 'test']
			worksheets = recent_worksheets(self.user)
			print worksheets
		assert False
