import mock

from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

from ..worksheet_utils import recent_worksheets


User = get_user_model()


class WorksheetHelperTests(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="organizer", password="pass")

	def test_recent_worksheets(self):
		with mock.patch('apps.common.worksheet_utils.BundleService.worksheets') as worksheet_endpoint_mock:
			worksheet_endpoint_mock.return_value = [
				{
					'id': 1,
					'uuid': 1,
					'name': 'test',
					'owner_name': self.user.username
				}
			]
			worksheets = recent_worksheets(self.user)
			self.assertEquals(len(worksheets), 1)
			uuid, name, owner_name = worksheets[0]
			self.assertEquals(uuid, 1)
			self.assertEquals(name, 'test')
			self.assertEquals(owner_name, self.user.username)
