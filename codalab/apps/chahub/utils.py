from django.conf import settings

import logging
import os
import requests
import json

logger = logging.getLogger(__name__)


def send_to_chahub(endpoint, raw_data):
    """
    Does a post request to the specified API endpoint on chahub with the inputted data.
    :param endpoint: String designating which API endpoint; IE: 'producers/'
    :param raw_data: Dictionary containing data we are sending away to the endpoint.
    :return:
    """
    try:
        _chahub_api_url_check()
    except KeyError:
        logger.info("CHAHUB_API_URL not defined in settings!")
        return

    chahub_online = _chahub_online_check()

    if not chahub_online:
        logger.info("Chahub is currently offline. Cancelling.")
        raise requests.ConnectionError("Chahub is currently offline. Please try again later.")

    url = "{}{}".format(settings.CHAHUB_API_URL, endpoint)

    data = json.dumps(raw_data)

    try:
        _chahub_send_data(url, data)
    except requests.ConnectionError:
        logger.info("Unable to POST data to Chahub. There was an error, please try again.")


def _chahub_api_url_check():
    """
    Helper that simply raises an error if CHAHUB_API_URL is not defined
    :return:
    """
    if not settings.CHAHUB_API_URL:
        raise KeyError("CHAHUB_API_URL not defined in settings!")

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

def _chahub_send_data(url, data):
    """
    Helper to send data to Chahub
    :param url: String URL
    :param data: Dictionary Data
    :return:
    """
    logger.info("ChaHub :: Sending to ChaHub ({}) the following data: \n{}".format(url, data))
    try:
        requests.post(url, data, headers={
            'Content-type': 'application/json',
            'X-CHAHUB-API-KEY': settings.CHAHUB_API_KEY,
        })
    except requests.ConnectionError:
        raise requests.ConnectionError("Unbale to POST data to Chahub. There was an error, please try again.")
