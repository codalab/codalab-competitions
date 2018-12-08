import datetime
import mock
from django.conf import settings

from django.test import TestCase
from django.test.utils import override_settings

from apps.authenz.models import ClUser
from apps.web.models import CompetitionSubmission, Competition, CompetitionPhase, CompetitionParticipant, \
    ParticipantStatus
from apps.web.tasks import send_chahub_general_stats


class ChahubUtillityTests(TestCase):
    def setUp(self):
        self.user = ClUser.objects.create_user(username="user", password="pass")
        self.competition = Competition.objects.create(
            title="Test Competition",
            creator=self.user,
            modified_by=self.user,
            published=True,
        )
        self.participant = CompetitionParticipant.objects.create(
            user=self.user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0],
        )
        self.phase = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )

    @override_settings(CHAHUB_API_URL='http://host.docker.internal/')
    def test_send_to_chahub_utillity(self):
        # with mock.patch('apps.web.models.CompetitionSubmission.send_to_chahub') as send_to_chahub_mock:
        with mock.patch('apps.web.tasks.send_to_chahub') as send_to_chahub_mock:
            send_to_chahub_mock.return_value = None
            # Calling this as a function instead of a task?
            send_chahub_general_stats()
            # attempts to send to Chahub once
            # We succesfully sent data to Chahub
            assert send_to_chahub_mock.called

