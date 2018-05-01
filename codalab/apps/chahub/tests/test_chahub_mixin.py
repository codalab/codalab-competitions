import datetime
import mock

from django.test import TestCase

from apps.authenz.models import ClUser
from apps.web.models import CompetitionSubmission, Competition, CompetitionPhase, CompetitionParticipant, \
    ParticipantStatus


class ChahubMixinTests(TestCase):

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


    def test_submission_mixin_save_only_retries_once(self):
        submission = CompetitionSubmission(phase=self.phase, participant=self.participant)
        with mock.patch('apps.web.models.CompetitionSubmission.send_to_chahub') as send_to_chahub_mock:
            send_to_chahub_mock.return_value = None
            submission.save()
            # attempts to send to Chahub once
            assert send_to_chahub_mock.called

            # reset
            send_to_chahub_mock.called = False

            # does not call again
            submission.save()
            assert not send_to_chahub_mock.called
