import json
import requests

from django.db import models
from django.utils import timezone


class ChaHubSaveMixin(object):
    """Helper mixin for saving model data to ChaHub.

    To use:
    1) Override `get_chahub_url()` to return the endpoint URL on ChaHub for this model
    2) Override `get_chahub_data()` to return a dictionary to send to ChaHub
    3) Data is sent on `save()` and `sent_to_chahub` timestamp is set

    To update remove the `sent_to_chahub` timestamp and call `save()`"""
    # This is set whenever a successful update happens
    sent_to_chahub = models.DateTimeField(null=True, blank=True)

    def get_chahub_url(self):
        """Override this to return the endpoint URL for this resource

        Example:
            return "http://localhost:8001/api/v1/competitions/"
        """
        raise NotImplementedError()

    def get_chahub_data(self):
        """Override this to return a dictionary with data to send to chahub

        Example:
            return {"name": self.name}
        """
        raise NotImplementedError()

    def send_to_chahub(self):
        """Sends data to chahub and returns the HTTP response"""
        url = self.get_chahub_url()
        data = json.dumps(self.get_chahub_data())
        resp = requests.post(url, data)
        if resp.status_code in (200, 201):
            self.sent_to_chahub = timezone.now()

    def save(self, *args, **kwargs):
        if not self.sent_to_chahub:
            self.send_to_chahub()
        return super(ChaHubSaveMixin).save(*args, **kwargs)
