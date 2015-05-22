import mock
from unittest import TestCase

from django.contrib.auth import get_user_model
from django.forms import ValidationError

from apps.authenz.adapter import CodalabAccountAdapter


User = get_user_model()


class TestRestrictedUsernames(TestCase):
    OK_USERNAMES = ['john', "test.man", "one_mo_time-again"]
    BAD_USERNAME = ['@#@#DFAFDA', "gmail@gmail.com", "testing-omg./wut"]

    def setUp(self):
        super(TestRestrictedUsernames, self).setUp()
        self.adapter = CodalabAccountAdapter()

    def test_username_with_valid_characters_works(self):
        for valid_name in self.OK_USERNAMES:
            self.assertTrue(self.adapter.clean_username(valid_name))

    def test_username_can_only_contain_certain_characters(self):
        # a-zA-Z0-9.-_ are the only allowed characters in a username
        for invalid_name in self.BAD_USERNAME:
            with self.assertRaises(ValidationError):
                self.adapter.clean_username(invalid_name)

    def test_username_cannot_be_on_blacklist(self):
        # blacklist is already tested by allauth. Testing for our adaptor.
        with mock.patch('apps.authenz.adapter.app_settings') as app_settings_mock:
            app_settings_mock.USERNAME_BLACKLIST = ["a_restricted_name"]
            with self.assertRaises(ValidationError):
                self.adapter.clean_username("a_restricted_name")

    def test_username_cannot_be_taken(self):
        User.objects.create_user("test_name_should_be_taken", "pass")
        with self.assertRaises(ValidationError):
            self.adapter.clean_username("test_name_should_be_taken")
