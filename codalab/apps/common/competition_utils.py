'''
This file contains utilities for competitions
'''
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