import json
import requests

from django.contrib.auth import get_user_model
from codalab import settings

User = get_user_model()


def run():
    if all([settings.MAILCHIMP_MEMBERS_ENDPOINT_ALL, settings.MAILCHIMP_API_KEY]):
        for user in User.objects.all():
            data = {
                "email_address": user.email,
                "status": "subscribed",
            }

            r = requests.patch(
                settings.MAILCHIMP_MEMBERS_ENDPOINT_ALL,
                auth=("", settings.MAILCHIMP_API_KEY),
                data=json.dumps(data)
            )

            if not r.ok:
                requests.post(
                    settings.MAILCHIMP_MEMBERS_ENDPOINT_ALL,
                    auth=("", settings.MAILCHIMP_API_KEY),
                    data=json.dumps(data)
                )
