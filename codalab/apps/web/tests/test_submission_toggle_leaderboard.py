import datetime
import mock

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model

from apps.web.models import (Competition,
                             CompetitionParticipant,
                             CompetitionPhase,
                             CompetitionSubmission,
                             CompetitionSubmissionStatus,
                             ParticipantStatus,
                             PhaseLeaderBoard,
                             PhaseLeaderBoardEntry,
                             add_submission_to_leaderboard)

User = get_user_model()


class SubmissionToggleLeaderboardTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="organizer", password="pass")
        self.participant_user = User.objects.create_user(username="participant", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")
        self.competition = Competition.objects.create(creator=self.organizer, modified_by=self.organizer, published=True)
        self.participant_1 = CompetitionParticipant.objects.create(
            user=self.participant_user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.organizer_participant = CompetitionParticipant.objects.create(
            user=self.organizer,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.phase_1 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )

        submission_finished = CompetitionSubmissionStatus.objects.create(name="finished", codename="finished")
        submission_failed = CompetitionSubmissionStatus.objects.create(name="failed", codename="failed")

        self.submission_1 = CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=29)
        )
        self.submission_2 = CompetitionSubmission.objects.create(
            participant=self.organizer_participant,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=29)
        )
        self.submission_3 = CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_failed,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=29)
        )

        self.submission_1.status = submission_finished
        self.submission_1.save()
        self.submission_2.status = submission_finished
        self.submission_2.save()
        self.submission_3.status = submission_failed
        self.submission_3.save()

        add_submission_to_leaderboard(self.submission_2)

        self.client = Client()
        self.url = reverse("competitions:submission_toggle_leaderboard", kwargs={"submission_pk": self.submission_1.pk})

    def test_toggle_leaderboard_returns_404_if_not_competition_owner(self):
        self.client.login(username="other", password="pass")
        resp = self.client.post(self.url)
        self.assertEquals(resp.status_code, 404)

    def test_toggle_leaderboard_returns_404_if_participant_not_owner(self):
        self.client.login(username="participant", password="pass")
        resp = self.client.post(self.url)
        self.assertEquals(resp.status_code, 404)

    def test_toggle_leaderboard_returns_200_and_removes_submission_from_leaderboard(self):
        add_submission_to_leaderboard(self.submission_1)
        self.client.login(username="organizer", password="pass")
        resp = self.client.post(self.url)
        self.assertEquals(resp.status_code, 200)
        submission_exists_on_leaderboard = PhaseLeaderBoardEntry.objects.filter(
            result=self.submission_1
        ).exists()
        self.assertFalse(submission_exists_on_leaderboard)

        # Make sure the other submission remains untouched
        self.assertTrue(PhaseLeaderBoardEntry.objects.get(result=self.submission_2))

    def test_toggle_leaderboard_returns_200_and_adds_submission_to_leaderboard(self):
        self.client.login(username="organizer", password="pass")
        resp = self.client.post(self.url)
        self.assertEquals(resp.status_code, 200)
        submission_exists_on_leaderboard = PhaseLeaderBoardEntry.objects.filter(
            board__phase=self.submission_1.phase,
            result=self.submission_1
        ).exists()
        self.assertTrue(submission_exists_on_leaderboard)

        # Make sure the other submission remains untouched
        self.assertTrue(PhaseLeaderBoardEntry.objects.get(result=self.submission_2))

    def test_toggle_leaderboard_returns_400_if_submission_was_not_marked_finished(self):
        # Any submission that is not status = Finished should fail, submission_3 is marked 'failed'
        self.client.login(username="organizer", password="pass")
        url = reverse("competitions:submission_toggle_leaderboard", kwargs={"submission_pk": self.submission_3.pk})
        resp = self.client.post(url)
        self.assertEquals(resp.status_code, 400)
