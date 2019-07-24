import mock
import requests
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.newsletter.models import NewsletterSubscription
from django.conf import settings

from apps.newsletter.tasks import retry_mailing_list

User = get_user_model()


class CustomResponse:
    def __init__(self, status=200, detail=None):
        self.status = status
        self.detail = 'The requested resource could not be found' if detail is None else detail
        self.ok = str(self.status).startswith('2')

    def json(self):
        return {'detail': self.detail}


class NewsletterOptIn(TestCase):
    def setUp(self):
        self.user = User(email='test@user.com', username='testuser', is_active=True)
        self.other_user = User(email='other@user.com', username='otheruser')
        self.newsletter_subscription = NewsletterSubscription(email='test@user.com')
        settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER = 'doesnt-matter'
        settings.MAILCHIMP_API_KEY = 'doesnt-matter'

    def tearDown(self):
        settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER = None
        settings.MAILCHIMP_API_KEY = None

    def mock_save_user(self, post_status_code, patch_status_code, user=None, response_detail=None, exception=False):
        user = self.user if user is None else user
        post_response = CustomResponse(status=post_status_code)
        patch_response = CustomResponse(status=patch_status_code, detail=response_detail)

        with mock.patch('apps.newsletter.models.requests.post') as mock_post:
            mock_post.return_value = post_response
            if exception:
                mock_post.side_effect = requests.exceptions.RequestException
            with mock.patch('apps.newsletter.models.requests.patch') as mock_patch:
                mock_patch.return_value = patch_response
                if exception:
                    mock_patch.side_effect = requests.exceptions.RequestException
                user.save()
                return mock_post, mock_patch

    def mock_retry_mailing_list(self, get_status_code):
        get_response = CustomResponse(status=get_status_code)
        with mock.patch('apps.newsletter.models.NewsletterSubscription.subscribe') as mock_subscribe:
            with mock.patch('apps.newsletter.models.NewsletterSubscription.unsubscribe') as mock_unsubscribe:
                with mock.patch('apps.newsletter.tasks.requests.get') as mock_get:
                    mock_get.return_value = get_response
                    retry_mailing_list()
                    return mock_subscribe, mock_unsubscribe

    def test_user_creation_with_opt_in_creates_newsletter_subscription(self):
        self.user.newsletter_opt_in = True
        mock_post, mock_patch = self.mock_save_user(patch_status_code=400, post_status_code=200)
        assert mock_post.called
        assert mock_patch.called
        assert NewsletterSubscription.objects.filter(email=self.user.email).exists()
        newsletter_user = NewsletterSubscription.objects.get(email=self.user.email)
        assert not newsletter_user.needs_retry
        assert newsletter_user.subscription_active

    def test_user_creation_without_opt_in_does_not_create_newsletter_subscription(self):
        self.user.newsletter_opt_in = False
        self.mock_save_user(patch_status_code=200, post_status_code=200)
        assert User.objects.filter(email=self.user.email).exists()
        assert not NewsletterSubscription.objects.filter(email=self.user.email).exists()

    def test_user_unsubscribed_from_mailing_list(self):
        # Subscribe the user
        self.user.newsletter_opt_in = True
        self.mock_save_user(patch_status_code=400, post_status_code=200)
        assert NewsletterSubscription.objects.filter(email=self.user.email).exists()
        # Unsubscribe the user
        self.user.newsletter_opt_in = False
        self.mock_save_user(patch_status_code=200, post_status_code=400)
        assert not NewsletterSubscription.objects.filter(email=self.user.email).exists()

    def test_create_user_newsletter_is_active_false(self):
        self.user.newsletter_opt_in = True
        self.user.is_active = False
        self.mock_save_user(patch_status_code=400, post_status_code=400)
        assert not NewsletterSubscription.objects.filter(email=self.user.email).exists()

    def test_retry_mailing_list(self):
        self.newsletter_subscription.subscription_active = False
        self.newsletter_subscription.needs_retry = True
        self.newsletter_subscription.save()
        mock_subscribe, mock_unsubscribe = self.mock_retry_mailing_list(get_status_code=200)
        assert not mock_subscribe.called
        assert mock_unsubscribe.called

        self.newsletter_subscription.subscription_active = True
        self.newsletter_subscription.needs_retry = True
        self.newsletter_subscription.save()
        mock_subscribe, mock_unsubscribe = self.mock_retry_mailing_list(get_status_code=200)
        assert mock_subscribe.called
        assert not mock_unsubscribe.called

    def test_mailing_list_needs_retry_on_patch_fail_with_empty_detail(self):
        self.user.newsletter_opt_in = True
        mock_post, mock_patch = self.mock_save_user(patch_status_code=400, post_status_code=400, response_detail='')
        assert mock_patch.called
        assert not mock_post.called
        assert NewsletterSubscription.objects.filter(email=self.user.email).exists()
        newsletter_user = NewsletterSubscription.objects.get(email=self.user.email)
        assert newsletter_user.needs_retry
        assert newsletter_user.subscription_active

    def test_mailing_list_needs_retry_on_patch_fail_with_detail(self):
        self.user.newsletter_opt_in = True
        mock_post, mock_patch = self.mock_save_user(patch_status_code=400, post_status_code=400)
        assert mock_patch.called
        assert mock_post.called
        assert NewsletterSubscription.objects.filter(email=self.user.email).exists()
        newsletter_user = NewsletterSubscription.objects.get(email=self.user.email)
        assert newsletter_user.needs_retry
        assert newsletter_user.subscription_active

    def test_mailing_list_needs_retry_on_unsubscribe_patch_fail(self):
        self.newsletter_subscription.save()
        assert NewsletterSubscription.objects.filter(email=self.user.email).exists()
        self.user.newsletter_opt_in = False
        mock_post, mock_patch = self.mock_save_user(patch_status_code=400, post_status_code=400)
        assert mock_patch.called
        assert not mock_post.called
        assert NewsletterSubscription.objects.filter(email=self.user.email).exists()
        newsletter_user = NewsletterSubscription.objects.get(email=self.user.email)
        assert newsletter_user.needs_retry
        assert not newsletter_user.subscription_active

    def test_mailing_list_needs_retry_on_request_error(self):
        self.user.newsletter_opt_in = True
        self.mock_save_user(patch_status_code=200, post_status_code=200, exception=True)
        assert NewsletterSubscription.objects.filter(email=self.user.email).exists()
        assert NewsletterSubscription.objects.get(email=self.user.email).needs_retry
