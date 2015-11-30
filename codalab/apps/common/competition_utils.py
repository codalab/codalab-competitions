'''
This file contains utilities for competitions
'''
from random import randint

from django.db.models import Count

from apps.web.models import Competition


def get_most_popular_competitions(limit=3):
	'''
	Function to return most popular competitions
	1.  Will return three most popular comptitions, if any
	'''
	competitions = Competition.objects.filter(published=True) \
    .annotate(num_participants=Count('participants')) \
	.order_by('-num_participants')

	if len(competitions) < 3:
		return competitions

	return competitions[:limit]


def get_featured_competitions(limit=3):
	'''
	Function to return featured competitions
	1. It will return three random active competitions
	2. Declare featured competitions list
	3. Get all competition that are published
	4. Get popular competitions
	5. Get popular competitions pk
	6. Exclude popular competitions from queryset
	7. Check if queryset is greater than 3; if not, return queryset
	8. If queryset is greater than 3, return 3 randomly
	'''
	featured_competitions = []
	competitions = Competition.objects.filter(published=True)
	popular_competitions = get_most_popular_competitions()
	popular_competitions_pk = [c.pk for c in popular_competitions]
	competitions = competitions.exclude(pk__in=popular_competitions_pk)

	if len(competitions) < 3:
		return competitions
	else:
		for _ in range(0, 3):
			competition = competitions[randint(0, competitions.count() - 1)]
			featured_competitions.append(competition)

	return featured_competitions