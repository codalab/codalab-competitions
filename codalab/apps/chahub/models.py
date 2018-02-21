import hashlib
import json
import logging
import requests

from django.conf import settings
from django.db import models
from django.utils import timezone


logger = logging.getLogger(__name__)


class ChaHubSaveMixin(models.Model):
    """Helper mixin for saving model data to ChaHub.

    To use:
    1) Override `get_chahub_endpoint()` to return the endpoint on ChaHub API for this model
    2) Override `get_chahub_data()` to return a dictionary to send to ChaHub
    3) Data is sent on `save()` and `sent_to_chahub` timestamp is set

    To update remove the `sent_to_chahub` timestamp and call `save()`"""
    # Timestamp set whenever a successful update happens
    sent_to_chahub = models.DateTimeField(null=True, blank=True)

    # A hash of the last json information that was sent to avoid sending duplicate information
    chahub_data_hash = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    # -------------------------------------------------------------------------
    # METHODS TO OVERRIDE WHEN USING THIS MIXIN!
    # -------------------------------------------------------------------------
    def get_chahub_endpoint(self):
        """Override this to return the endpoint URL for this resource

        Example:
            # If the endpoint is chahub.org/api/v1/competitions/ then...
            return "competitions/"
        """
        raise NotImplementedError()

    def get_chahub_data(self):
        """Override this to return a dictionary with data to send to chahub

        Example:
            return {"name": self.name}
        """
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    # Regular methods
    # -------------------------------------------------------------------------
    def get_chahub_url(self):
        assert settings.CHAHUB_API_URL, "No ChaHub URL given, cannot send details to ChaHub"
        assert settings.CHAHUB_API_URL.endswith("/"), "ChaHub API url must end with a slash"

        endpoint = self.get_chahub_endpoint()
        assert endpoint, Exception("No ChaHub API endpoint given")

        return "{}{}".format(settings.CHAHUB_API_URL, endpoint)

    def send_to_chahub(self, data):
        """Sends data to chahub and returns the HTTP response"""
        url = self.get_chahub_url()

        logger.info("ChaHub :: Sending to ChaHub ({}) the following data: \n{}".format(url, data))

        try:
            return requests.post(url, data, headers={
                'Content-type': 'application/json',
                'X-CHAHUB-API-KEY': settings.CHAHUB_API_KEY,
            })
        except requests.ConnectionError:
            return None

    def save(self, *args, **kwargs):
        if settings.CHAHUB_API_URL:
            data = json.dumps(self.get_chahub_data())
            data_hash = hashlib.md5(data).hexdigest()

            if not self.sent_to_chahub or self.chahub_data_hash != data_hash:
                resp = self.send_to_chahub(data)

                logger.info("ChaHub :: Received response {} {}".format(resp.status_code, resp.content))

                if resp and resp.status_code in (200, 201):
                    self.sent_to_chahub = timezone.now()
                    self.chahub_data_hash = data_hash

        super(ChaHubSaveMixin, self).save(*args, **kwargs)
