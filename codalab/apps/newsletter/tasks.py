import logging

import requests
from celery import task
from django.conf import settings

from apps.newsletter.models import NewsletterSubscription

logger = logging.getLogger(__name__)

@task(queue='site-worker', soft_time_limit=60 * 5)
def retry_mailing_list():
    if all([settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER, settings.MAILCHIMP_API_KEY]):
        response = requests.get(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_NEWSLETTER,
            auth=("", settings.MAILCHIMP_API_KEY),
        )

        if response.ok:
            retry_items = NewsletterSubscription.objects.filter(needs_retry=True)
            if retry_items:
                for item in retry_items:
                    item.retry()
        else:
            logger.info("Mailchimp endpoint could not be reached at this time. "
                        "This task will be run again in 60 minutes.")

    else:
        logger.info("Settings not found for Mailchimp endpoint and API. Please"
                    "add these to your Django settings file. This task will be run again in 60 minutes.")
