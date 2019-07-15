from celery import task

from apps.newsletter.models import NewsletterSubscription


@task(queue='site-worker', soft_time_limit=60 * 5)
def retry_mailing_list():
    retry_items = NewsletterSubscription.objects.filter(needs_retry=True)
    if retry_items:
        for item in retry_items:
            item.retry()
