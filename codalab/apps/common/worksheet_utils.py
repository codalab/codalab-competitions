'''
This file contains utilities specific to worksheets.
'''
import random
from django.conf import settings
from apps.web.bundles import BundleService

def get_worksheets(request_user, limit=3):
    '''
    Get worksheets to display on the front page.
    Keep only |worksheet_uuids|.
    '''
    service = BundleService(request_user)

    # Select good high-quality worksheets
    list_worksheets = service.search_worksheets(['tag=paper,software,data'])

    # Reformat
    list_worksheets = [(val['uuid'], val.get('title') or val['name'], val['name'], val['owner_name']) for val in list_worksheets]

    # Randomly choose some
    list_worksheets = random.sample(list_worksheets, min(limit, len(list_worksheets)))

    return list_worksheets


def recent_worksheets(request_user, limit=3):
    """Used for worksheets in competitions. Issue 1014"""
    # TODO: deprecate this
    service = BundleService(request_user)
    unsorted_worksheets = service.worksheets()


    #if not worksheets:
    #   return worksheets  # just incase the list is empty

    sorted_worksheets = sorted(unsorted_worksheets, key=lambda k: k['id'], reverse=True)
    worksheets = [(val['uuid'], val['name'], val['owner_name']) for val in sorted_worksheets]
    return worksheets[0:limit]
