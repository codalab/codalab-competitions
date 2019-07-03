import hashlib
import json

import requests
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.newsletter.models import NewsletterUser
from codalab import settings

User = get_user_model()


class NewsletterOptIn(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@user.com', username='testuser')
        self.other_user = User.objects.create(email='other@user.com', username='otheruser')
        self.newsletter_user = NewsletterUser.objects.create(email='test@user.com')

    def tearDown(self):
        user_hash = hashlib.md5(self.user.email)
        get_status = requests.get(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
            auth=("", settings.MAILCHIMP_API_KEY),
        )

        if get_status.ok:
            delete_status = requests.delete(
                settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
                auth=("", settings.MAILCHIMP_API_KEY),
            )

            if delete_status.ok:
                print('Test user has been deleted from the Mailchimp mailing list')
            else:
                print('Could not delete this user from the Mailchimp mailing list')
        else:
            print('User was not found on the Mailchimp mailing list')

    def test_create_user_newsletter_opt_in_true(self):
        self.user.newsletter_opt_in = True
        self.user.save()
        assert NewsletterUser.objects.filter(email=self.user.email).exists()

        user_hash = hashlib.md5(self.user.email)

        get_status = requests.get(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
            auth=("", settings.MAILCHIMP_API_KEY),
        )

        assert get_status.ok

    def test_create_user_newsletter_opt_in_false(self):
        self.other_user.newsletter_opt_in = False
        self.other_user.save()
        assert not NewsletterUser.objects.filter(email=self.other_user.email).exists()

        user_hash = hashlib.md5(self.other_user.email)

        get_status = requests.get(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
            auth=("", settings.MAILCHIMP_API_KEY),
        )

        assert not get_status.ok

    def test_newsletteruser_deleted(self):
        user_hash = hashlib.md5(self.newsletter_user.email)
        self.newsletter_user.delete()

        get_status = requests.get(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
            auth=("", settings.MAILCHIMP_API_KEY),
        )

        json_status = get_status.json()

        assert json_status['status'] == u'unsubscribed'

    def test_user_unsubscribed_from_mailing_list(self):
        # User subscribes to the mailing list here
        self.user.newsletter_opt_in = True
        self.user.save()

        assert NewsletterUser.objects.filter(email=self.user.email).exists()

        user_hash = hashlib.md5(self.user.email)

        get_status = requests.get(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
            auth=("", settings.MAILCHIMP_API_KEY),
        )

        assert get_status.ok

        # User unsubscribes to the mailing list here
        self.user.newsletter_opt_in = False
        self.user.save()
        assert not NewsletterUser.objects.filter(email=self.user.email).exists()

        data = {
            "status": "unsubscribed",
        }
        requests.patch(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
            auth=("", settings.MAILCHIMP_API_KEY),
            data=json.dumps(data)
        )

        get_status = requests.get(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
            auth=("", settings.MAILCHIMP_API_KEY),
        )

        json_status = get_status.json()

        assert json_status['status'] == u'unsubscribed'
