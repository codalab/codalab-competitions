import mock
from django.test import TestCase
# from codalabtools.compute.worker import docker_prune
#
#
# class DockPruneTests(TestCase):
#     def _dockertestsize(self, size_mock):
#         with mock.patch('os.system') as mock_os_system:
#             with mock.patch('codalabtools.compute.worker.docker_get_size') as mock_get_size:
#                 mock_get_size.return_value = size_mock
#                 docker_prune()
#                 return mock_os_system.called
#
#     def test_only_prune_if_larger_than_settings_value(self):
#         self.assertEquals(self._dockertestsize("15.0GB"), 1)  # High value
#         self.assertEquals(self._dockertestsize("0.0GB"), 0)  # Low value
#         self.assertEquals(self._dockertestsize("5.0GB"), 0)  # Moderate value
#         self.assertEquals(self._dockertestsize("-10.0GB"), 0)  # Neg value

