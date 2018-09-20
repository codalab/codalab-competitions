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
        self.user1 = User.objects.create(email="user@test.com", username="user", password="pass")
        self.user2 = User.objects.create(email="user2@test.com", username="user2", password="pass")
        self.user3 = User.objects.create(email="user3@test.com", username="user3", password="pass")
        self.user4 = User.objects.create(email="user4@test.com", username="user4", password="pass")
        self.user5 = User.objects.create(email="user5@test.com", username="user5", password="pass")

        self.competition1 = Competition.objects.create(creator=self.user, modified_by=self.user, published=True)
        self.competition2 = Competition.objects.create(creator=self.user, modified_by=self.user, published=True)
        self.competition3 = Competition.objects.create(creator=self.user, modified_by=self.user, published=True)
        self.competition4 = Competition.objects.create(creator=self.user, modified_by=self.user, published=True)
        self.competition5 = Competition.objects.create(creator=self.user, modified_by=self.user, published=True)

        self.participant1 = CompetitionParticipant.objects.create(
            user=self.user,
            competition=self.competition1,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )

        self.phase1 = CompetitionPhase.objects.create(
            competition=self.competition1,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )

        submission_finished = CompetitionSubmissionStatus.objects.create(name="finished", codename="finished")

        self.submission1 = CompetitionSubmission.objects.create(
            participant=self.participant1,
            phase=self.phase1,
            status=submission_finished,
            submitted_at=now() - datetime.timedelta(days=29),
            description=u"Some description with unicode \u2020"
        )

    def test_get_featured_competitions_returns_competition_with_1_submission_past_week(self):
        competitions = get_featured_competitions()
        # Should only return #1 because it is the only one with a submission
        assert len(competitions) == 1
        assert competitions[0].pk == self.competition1.pk

    def test_get_featured_competitions_returns_competition_started_one_month_ago(self):
        old_competition = Competition.objects.create(
            creator=self.user,
            modified_by=self.user,
            published=True,
            start_date=now() - datetime.timedelta(days=31)
        )
        competitions = get_featured_competitions()
        # Should only have the 5 original competitions not the older competition
        assert len(competitions) == 5
        assert old_competition.pk not in [c.pk for c in competitions]
