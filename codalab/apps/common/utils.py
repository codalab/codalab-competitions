import random

from django.conf import settings


def random_worksheets(list_worksheets):
    """Function to return most random worksheets, if any"""

    if not list_worksheets:
        return list_worksheets  # just incase the list is empty

    list_worksheets = [(val['uuid'], val['name'], val['owner_name']) for val in list_worksheets if val['uuid'] in settings.FRONTPAGE_WORKSHEET_UUIDS ]

    if len(list_worksheets) <= 2:
        return list_worksheets
    else:
        list_worksheets = random.sample(list_worksheets, 3)
        return list_worksheets
