import hashlib
import json

import requests
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from codalab import settings


class NewsletterUser(models.Model):
    email = models.EmailField(null=True, blank=True, default=None)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


@receiver(pre_delete, sender=NewsletterUser)
def newsletteruser_unsubscribe(instance, **kwargs):
    data = {
        "status": "unsubscribed",
    }

    user_hash = hashlib.md5(str.lower(instance.email.encode()))

    # Update user in Mailchimp to Unsubscribed
    requests.patch(
        settings.MAILCHIMP_MEMBERS_ENDPOINT + '/' + user_hash.hexdigest(),
        auth=("", settings.MAILCHIMP_API_KEY),
        data=json.dumps(data)
    )


class Newsletter(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Published', 'Published')
    )
    subject = models.CharField(max_length=250)
    body = models.TextField()
    email = models.ManyToManyField(NewsletterUser)
    status = models.CharField(max_length=10, choices=EMAIL_STATUS_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
