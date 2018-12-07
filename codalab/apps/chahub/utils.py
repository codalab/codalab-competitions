from django.conf import settings

import logging
import os
import requests
import json

logger = logging.getLogger(__name__)


def send_to_chahub(endpoint, data):
    """
    Does a post request to the specified API endpoint on chahub with the inputted data.
    :param endpoint: String designating which API endpoint; IE: 'producers/'
    :param data: Dictionary containing data we are sending away to the endpoint.
    :return:
    """

    assert settings.CHAHUB_API_URL

    if not _chahub_online_check():
        logger.info("Chahub is currently offline. Cancelling.")
        raise requests.ConnectionError("Chahub is currently offline. Please try again later.")

    url = "{}{}".format(settings.CHAHUB_API_URL, endpoint)

    data = json.dumps(data)

    logger.info("ChaHub :: Sending to ChaHub ({}) the following data: \n{}".format(url, data))
    try:
        requests.post(url, data, headers={
            'Content-type': 'application/json',
            'X-CHAHUB-API-KEY': settings.CHAHUB_API_KEY,
        })
    except requests.ConnectionError:
        raise requests.ConnectionError("Unbale to POST data to Chahub. There was an error, please try again.")


def _chahub_online_check():
    """
    Helper that simply checks if Chahub is online, and returns a boolean
    """
    logger.info("Checking whether ChaHub is online before sending retries")
    try:
        response = requests.get(settings.CHAHUB_API_URL)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        # This base exception works for HTTP errors, Connection errors, etc.
        return False
