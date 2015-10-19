import random

from django.conf import settings

from apps.web.bundles import BundleService


def random_worksheets(request_user, limit=3):
    """Function to return most random worksheets, if any"""
    service = BundleService(request_user)
    list_worksheets = service.worksheets()

    if not list_worksheets:
        return list_worksheets  # just incase the list is empty

    list_worksheets = [(val['uuid'], val['name'], val['owner_name']) for val in list_worksheets if val['uuid'] in settings.FRONTPAGE_WORKSHEET_UUIDS ]

    if len(list_worksheets) <= 2:
        return list_worksheets
    else:
        list_worksheets = random.sample(list_worksheets, 3)
        return list_worksheets


def recent_worksheets(request_user, limit=3):
    """Function to return most recent worksheets"""
    service = BundleService(request_user)
    unsorted_worksheets = service.worksheets()

    #if not worksheets:
    #	return worksheets  # just incase the list is empty

    sorted_worksheets = sorted(unsorted_worksheets, key=lambda k: k['id'], reverse=True)
    worksheets = [(val['uuid'], val['name'], val['owner_name']) for val in sorted_worksheets]
    return worksheets[0:limit]
