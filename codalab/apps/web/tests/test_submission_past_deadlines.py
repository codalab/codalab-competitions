import datetime

import pytest
from django.core.exceptions import PermissionDenied
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from apps.web.models import (Competition,
                             CompetitionParticipant,
                             ParticipantStatus,
                             CompetitionSubmission,
                             CompetitionPhase,
                             CompetitionSubmissionStatus)

User = get_user_model()


class CompetitionTestDeadlines(TestCase):

    def setUp(self):
        self.organizer_user = User.objects.create_user(username="organizer", password="pass")
        self.participant_user = User.objects.create_user(username="participant", password="pass")
        self.competition = Competition.objects.create(
            title="Test Competition",
            creator=self.organizer_user,
            modified_by=self.organizer_user,
            end_date=datetime.datetime.now() - datetime.timedelta(days=20),
            published=False
        )

        self.participant_1 = CompetitionParticipant.objects.create(
            user=self.participant_user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.phase_1 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=40),
        )
        self.phase_2 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=2,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
            auto_migration=True,
            phase_never_ends=True
        )

        self.client = Client()

    def test_competition_submission_past_end_if_phase_never_ends(self):
        # Submissions should be alllowed past competition end if the phase never ends
        self.client.login(username="participant", password="pass")
        submission_finished = CompetitionSubmissionStatus.objects.create(name="finished", codename="finished")

        try:
            self.submission_1 = CompetitionSubmission.objects.create(
                participant=self.participant_1,
                phase=self.phase_2,
                status=submission_finished,
                submitted_at=datetime.datetime.now()
            )
            pass
        except PermissionDenied:
            assert False, "We should not get to this line, submission should pass because phase never ends"

    def test_competition_submission_fails_past_end(self):
        # Submissions should be not be allowed past the end date if the phase does end
        self.client.login(username="participant", password="pass")
        submission_finished = CompetitionSubmissionStatus.objects.create(name="finished", codename="finished")

        with pytest.raises(PermissionDenied):
            self.submission_1 = CompetitionSubmission.objects.create(
                participant=self.participant_1,
                phase=self.phase_1,
                status=submission_finished,
                submitted_at=datetime.datetime.now()
            )
