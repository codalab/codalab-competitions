'''
This file contains utilities specific to worksheets.
'''
import random
from django.conf import settings
from apps.web.bundles import BundleService

def get_worksheets(request_user, worksheet_uuids, limit=3):
    '''
    Get worksheets to display on the front page.
    Keep only |worksheet_uuids|.
    '''
    service = BundleService(request_user)
    list_worksheets = service.worksheets()
    list_worksheets = [(val['uuid'], val.get('title') or val['name'], val['name'], val['owner_name']) for val in list_worksheets]

    # Filter only if it's non-empty.
    filtered_list_worksheets = [val for val in list_worksheets if val[0] in worksheet_uuids]
    if len(filtered_list_worksheets) > 0:
        list_worksheets = filtered_list_worksheets

    if len(list_worksheets) <= 2:
        return list_worksheets
    else:
        list_worksheets = random.sample(list_worksheets, 3)
        return list_worksheets


def recent_worksheets(request_user, limit=3):
    """Used for worksheets in competitions. Issue 1014"""
    service = BundleService(request_user)
    unsorted_worksheets = service.worksheets()


    #if not worksheets:
    #   return worksheets  # just incase the list is empty

    sorted_worksheets = sorted(unsorted_worksheets, key=lambda k: k['id'], reverse=True)
    worksheets = [(val['uuid'], val['name'], val['owner_name']) for val in sorted_worksheets]
    return worksheets[0:limit]
