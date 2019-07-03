import json
import requests

from django.contrib.auth import get_user_model
from codalab import settings

User = get_user_model()


def run():
    for user in User.objects.all():
        data = {
            "email_address": user.email,
            "status": "subscribed",
        }

        requests.patch(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_ALL,
            auth=("", settings.MAILCHIMP_API_KEY),
            data=json.dumps(data)
        )

        requests.post(
            settings.MAILCHIMP_MEMBERS_ENDPOINT_ALL,
            auth=("", settings.MAILCHIMP_API_KEY),
            data=json.dumps(data)
        )
