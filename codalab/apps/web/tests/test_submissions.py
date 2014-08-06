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
                             PhaseLeaderBoardEntry)

User = get_user_model()


class CompetitionSubmissionTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="organizer", password="pass")
        self.participant_user = User.objects.create_user(username="participant", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")
        self.competition = Competition.objects.create(creator=self.organizer, modified_by=self.organizer)
        self.participant_1 = CompetitionParticipant.objects.create(
            user=self.participant_user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.phase_1 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )

        submission_finished = CompetitionSubmissionStatus.objects.create(name="finished", codename="finished")

        self.submission_1 = CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=29)
        )

        self.client = Client()

    def test_delete_view_returns_404_if_not_competition_owner(self):
        self.client.login(username="other", password="pass")
        resp = self.client.post(reverse("competitions:submission_delete", kwargs={"pk": self.submission_1.pk}))
        self.assertEquals(resp.status_code, 404)

    def test_delete_view_returns_404_if_not_submission_owner(self):
        self.client.login(username="other", password="pass")
        resp = self.client.post(reverse("competitions:submission_delete", kwargs={"pk": self.submission_1.pk}))
        self.assertEquals(resp.status_code, 404)

    def test_delete_view_redirects_to_success_if_submission_owner(self):
        # There is currently no way for participants to delete their own submission, but I'll add this
        # behavior so it can be "switched on" easily later
        self.client.login(username="participant", password="pass")
        resp = self.client.post(reverse("competitions:submission_delete", kwargs={"pk": self.submission_1.pk}))
        self.assertRedirects(resp, reverse("competitions:view", kwargs={"pk": self.competition.pk}))

    def test_delete_view_redirects_to_success_if_competition_organizer_and_deletes_submission(self):
        self.client.login(username="organizer", password="pass")
        resp = self.client.post(reverse("competitions:submission_delete", kwargs={"pk": self.submission_1.pk}))
        self.assertRedirects(resp, reverse("competitions:view", kwargs={"pk": self.competition.pk}))
        self.assertEquals(0, len(CompetitionSubmission.objects.filter(pk=self.submission_1.pk)))

    def test_delete_view_returns_302_if_not_logged_in(self):
        resp = self.client.post(reverse("competitions:submission_delete", kwargs={"pk": self.submission_1.pk}))
        self.assertEquals(resp.status_code, 302)
