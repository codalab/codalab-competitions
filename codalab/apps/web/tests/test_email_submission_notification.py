# test that email matches participant user email
# test that email contains name of competition and link to it
# test that email outbox only contains 1 email

import datetime
import mock

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
# from django.core.urlresolvers import reverse

from apps.web.models import (Competition,
                             CompetitionParticipant,
                             CompetitionPhase,
                             CompetitionSubmission,
                             CompetitionSubmissionStatus,
                             ParticipantStatus
                             )
from .tasks import update_submission_task


User = get_user_model()


class SendEmailTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@user.com', username='testuser')
        self.other_user = User.objects.create(
            email='other@user.com', username='other')
        self.competition = Competition.objects.create(
            creator=self.user, modified_by=self.user)
        self.participant_1 = CompetitionParticipant.objects.create(
            user=self.user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(
                name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.participant_2 = CompetitionParticipant.objects.create(
            user=self.other_user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(
                name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.phase_1 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )
        self.phase_2 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=2,
            start_date=datetime.datetime.now() - datetime.timedelta(days=15),
            auto_migration=True
        )

        submission_finished = CompetitionSubmissionStatus.objects.create(
            name="finished", codename="finished")

        self.submission_1 = CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=29)
        )
        self.submission_2 = CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=28)
        )

        self.client = Client()

    def test_send_email_confirmation(self):
        sender = settings.DEFAULT_FROM_EMAIL
        receiver = self.user.email

        # mail.send_mail('Submission Confirmation', 'Submission has finished',
        #                sender, [receiver],
        #                fail_silently=False)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [receiver])
        self.assertEquals(mail.outbox[0].from_email, sender)
