'''
This file contains utilities specific to worksheets.
'''

def recent_worksheets(worksheets):
    '''
    Return the most recent worksheets (for featuring on the home page).
    TODO: return the title too.
    '''

    if not worksheets:
    	return worksheets  # just incase the list is empty

    sorted_worksheets = sorted(worksheets, key=lambda k: k['id'], reverse=True)

    if len(sorted_worksheets) <= 2:
        worksheets = [(val['uuid'], val['name'], val['owner_name']) for val in sorted_worksheets]
        return worksheets
    else:
        worksheets = sorted_worksheets[0:3]
        worksheets = [(val['uuid'], val['name'], val['owner_name']) for val in worksheets]
        return worksheets
