'''
This file contains utilities for competitions
'''
import datetime

from random import randint

from django.db.models import Count
from django.db.models import Q

from apps.web.models import Competition


def get_most_popular_competitions(limit=3):
    '''
    Function to return most popular competitions based on the amount of participants.

    :param limit: Amount of competitions to return. Default is 3.
    :rtype: list
    :return:  Most popular competitions.
    '''
    today = datetime.datetime.today()
    competitions = Competition.objects.filter(published=True) \
        .filter(Q(end_date__gte=today) | Q(end_date=None)) \
        .annotate(num_participants=Count('participants')) \
        .order_by('-num_participants') \
        .select_related('creator')

    if len(competitions) < 3:
        return competitions

    return competitions[:limit]


def get_featured_competitions(limit=3):
    '''
    Function to return featured competitions if they are still open.

    :param limit: Amount of competitionss to return. Default is 3
    :rtype: list
    :return: list of featured competitions
    '''
    today = datetime.datetime.today()
    featured_competitions = []
    competitions = Competition.objects.filter(published=True) \
        .filter(Q(end_date__gte=today)|Q(end_date=None)) \
        .annotate(num_participants=Count('participants')) \
        .select_related('creator')
    popular_competitions = get_most_popular_competitions()
    popular_competitions_pk = [c.pk for c in popular_competitions]
    competitions = competitions.exclude(pk__in=popular_competitions_pk)

    if len(competitions) < 3:
        return competitions
    else:
        while len(featured_competitions) < 3:
            competition = competitions[randint(0, competitions.count() - 1)]
            if competition not in featured_competitions:
                featured_competitions.append(competition)

    return featured_competitions