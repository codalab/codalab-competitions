import hashlib
import json

import requests
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import models as auth_models

from codalab import settings
from apps.newsletter.models import NewsletterSubscription


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
        if self.newsletter_opt_in and self.email and self.is_active:
            subscription, created = NewsletterSubscription.objects.get_or_create(email=self.email)
            if not subscription.subscription_active or subscription.needs_retry:
                subscription.subscribe()

        elif not self.newsletter_opt_in and self.email:
            subscription = NewsletterSubscription.objects.filter(email=self.email).first()
            if subscription:
                subscription.unsubscribe()

        super(ClUser, self).save(*args, **kwargs)


ClUser._meta.get_field('username').db_index = True
