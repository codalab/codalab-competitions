'''
This file contains utilities for competitions
'''
import datetime

from random import randint, shuffle, sample

from django.db.models import Count
from django.db.models import Q
from django.utils.timezone import now

from apps.web.models import Competition, CompetitionSubmission


def get_most_popular_competitions(min_participants=400, limit=5):
    today = datetime.datetime.today()
    competitions = Competition.objects.filter(published=True) \
        .filter(Q(end_date__gte=today) | Q(end_date=None)) \
        .annotate(num_participants=Count('participants')) \
        .filter(num_participants__gte=min_participants) \
        .order_by('?') \
        .select_related('creator')[:limit]
    # shuffle works in place, so turn competitions into list and shuffle it by reference
    competitions = list(competitions)
    shuffle(competitions)
    return competitions


def get_featured_competitions(popular_competitions_to_filter=None, limit=5):
    featured_competitions = []

    a_month_from_now = now() + datetime.timedelta(days=30)
    seven_days_ago = now() - datetime.timedelta(days=7)

    # Filter out competitions that don't have a submission from the last week
    recent_submissions = CompetitionSubmission.objects.filter(phase__competition__published=True, submitted_at__gte=seven_days_ago)
    recent_submissions = recent_submissions.select_related('phase', 'phase__competition')
    for sub in recent_submissions:
        # We have a recent submission, so check that competition is either active or has upcoming phase change
        competition = sub.phase.competition
        phase_change_within_a_month = competition.phases.filter(
            start_date__gte=now(),
            start_date__lte=a_month_from_now
        ).exists()
        if competition.is_active or phase_change_within_a_month:
            featured_competitions.append(competition)

    # Fill out competitions if we're missing any (or truncate if too much)
    featured_comp_count = len(featured_competitions)
    if featured_comp_count < limit:
        existing_pks = [c.pk for c in featured_competitions]
        random_competitions = Competition.objects.filter(published=True).exclude(pk__in=existing_pks)[:50]
        try:
            featured_competitions += sample(random_competitions, limit - featured_comp_count)
        except ValueError:
            # Eeep! We don't even have $limit competitions to choose from
            featured_competitions += list(random_competitions)
    elif featured_comp_count > limit:
        featured_competitions = featured_competitions[:limit]

    # Exclude popular competitions, so we don't show them near featured
    if popular_competitions_to_filter:
        filter_pks = [c.pk for c in popular_competitions_to_filter]
        featured_competitions = list(filter(lambda x: x.pk not in filter_pks, featured_competitions))

    # Random order each time
    shuffle(featured_competitions)

    return featured_competitions
