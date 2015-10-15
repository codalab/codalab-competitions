def recent_worksheets(worksheets):
    """Function to return most recent worksheets"""

    sorted_worksheets = sorted(worksheets, key=lambda k: k['id'], reverse=True)

    if len(sorted_worksheets) <= 2:
        worksheets = [(val['uuid'], val['name'], val['owner_name'])for val in sorted_worksheets]
        return worksheets
    else:
        worksheets = sorted_worksheets[0:3]
        worksheets = [(val['uuid'], val['name'], val['owner_name'])for val in worksheets]
        return worksheets
