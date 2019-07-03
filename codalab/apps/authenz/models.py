import hashlib
import json

import requests
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import models as auth_models

from codalab import settings
from apps.newsletter.models import NewsletterUser


class ClUser(auth_models.AbstractUser):
    """
    Base User model
    """
    # Notification settings
    participation_status_updates = models.BooleanField(default=True)
    organizer_status_updates = models.BooleanField(default=True)
    organizer_direct_message_updates = models.BooleanField(default=True)
    email_on_submission_finished_successfully = models.BooleanField(default=False)
    allow_forum_notifications = models.BooleanField(default=True)
    allow_admin_status_updates = models.BooleanField(default=True)
    newsletter_opt_in = models.BooleanField(default=False)

    # Profile details
    organization_or_affiliation = models.CharField(max_length=255, null=True, blank=True)

    team_name = models.CharField(max_length=64, null=True, blank=True)
    team_members = models.TextField(null=True, blank=True)

    method_name = models.CharField(max_length=20, null=True, blank=True)
    method_description = models.TextField(null=True, blank=True)
    project_url = models.URLField(null=True, blank=True)
    publication_url = models.URLField(null=True, blank=True)
    bibtex = models.TextField(null=True, blank=True)

    contact_email = models.EmailField(null=True, blank=True)

    rabbitmq_queue_limit = models.PositiveIntegerField(default=5, blank=True)
    rabbitmq_username = models.CharField(max_length=36, null=True, blank=True)
    rabbitmq_password = models.CharField(max_length=36, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.newsletter_opt_in and self.email:
            data = {
                "email_address": self.email,
                "status": "subscribed",
            }

            user_hash = hashlib.md5(str.lower(self.email.encode()))

            # Try to update the user before creating a new user
            update_user = requests.patch(
                settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
                auth=("", settings.MAILCHIMP_API_KEY),
                data=json.dumps(data)
            )

            # If no user is found in mailchimp, create a new mailing list user
            if not update_user.ok:
                requests.post(
                    settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER,
                    auth=("", settings.MAILCHIMP_API_KEY),
                    data=json.dumps(data)
                )

            # If there is no NewsletterUser for this user, create one
            if not NewsletterUser.objects.filter(email=self.email).exists():
                NewsletterUser.objects.create(email=self.email)

        elif not self.email and self.newsletter_opt_in:
            self.newsletter_opt_in = False
            raise ValidationError('You must have an email to receive the Codalab newsletter')

        elif not self.newsletter_opt_in and self.email:
            data = {
                "status": "unsubscribed",
            }

            user_hash = hashlib.md5(str.lower(self.email.encode()))

            # Update user in Mailchimp to Unsubscribed
            requests.patch(
                settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER + '/' + user_hash.hexdigest(),
                auth=("", settings.MAILCHIMP_API_KEY),
                data=json.dumps(data)
            )

            # Remove the user from the NewsletterUser model
            if NewsletterUser.objects.filter(email=self.email).exists():
                NewsletterUser.objects.get(email=self.email).delete()

        super(ClUser, self).save(*args, **kwargs)


ClUser._meta.get_field('username').db_index = True
