import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from ..competition_utils import get_featured_competitions
from apps.web.models import (Competition,
                             CompetitionParticipant,
                             ParticipantStatus, CompetitionPhase, CompetitionSubmission, CompetitionSubmissionStatus)

User = get_user_model()


class FeaturedCompetitionsTests(TestCase):

    def setUp(self):
        '''
        1. Create two different users
        2. Create few compettions where publised is True
        3. Add participants to competitions
        3. Return all competitions
        4. Return competitions with more participants
        '''

        self.user = User.objects.create(email="user1@tes.com", username="user1", password="pass")

        self.competition1 = Competition.objects.create(title="competition1", creator=self.user, modified_by=self.user, published=True)
        self.competition2 = Competition.objects.create(title="competition2", creator=self.user, modified_by=self.user, published=True)
        self.competition3 = Competition.objects.create(title="competition3", creator=self.user, modified_by=self.user, published=True)
        self.competition4 = Competition.objects.create(title="competition4", creator=self.user, modified_by=self.user, published=True)
        self.competition5 = Competition.objects.create(title="competition5", creator=self.user, modified_by=self.user, published=True)
        self.competition_old = Competition.objects.create(
            title="competition_old",
            creator=self.user,
            modified_by=self.user,
            published=True,
            start_date=now() - datetime.timedelta(days=50)
        )
        self.competition_oldest = Competition.objects.create(
            title="competition_oldest",
            creator=self.user,
            modified_by=self.user,
            published=True,
            start_date=now() - datetime.timedelta(days=500)
        )

        submission_finished = CompetitionSubmissionStatus.objects.create(name="finished", codename="finished")

        # First submission, new
        self.participant1 = CompetitionParticipant.objects.create(
            user=self.user,
            competition=self.competition1,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.phase1 = CompetitionPhase.objects.create(
            competition=self.competition1,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=29),  # less than 30 days
        )
        self.submission1 = CompetitionSubmission.objects.create(
            participant=self.participant1,
            phase=self.phase1,
            status=submission_finished,
        )
        self.submission1.submitted_at = now() - datetime.timedelta(days=5)  # less than 7 days old
        self.submission1.save()

        # Second submission, old
        self.participant2 = CompetitionParticipant.objects.create(
            user=self.user,
            competition=self.competition_old,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.phase2 = CompetitionPhase.objects.create(
            competition=self.competition_old,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=35),  # over 30 days old
        )
        self.submission2 = CompetitionSubmission.objects.create(
            participant=self.participant2,
            phase=self.phase2,
            status=submission_finished,
        )
        self.submission2.submitted_at = now() - datetime.timedelta(days=34)  # older than 30 days
        self.submission2.save()

    def test_get_featured_competitions_returns_newer_competitions(self):
        competitions = get_featured_competitions(limit=1)
        # Should always return the 1 new competition
        assert len(competitions) == 1
        assert self.competition_old not in competitions

        # Delete new competition, mark submission as newer, old competition should now appear in list
        self.competition1.delete()
        self.submission2.submitted_at = now()
        self.submission2.save()
        competitions = get_featured_competitions(limit=1)

        assert len(competitions) == 1
        assert self.competition_old in competitions
