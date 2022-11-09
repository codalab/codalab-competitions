import mock

from io import StringIO
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.core.management import call_command


class AddParticipantCommand(TestCase):

    def call_command(self, *args, **kwargs):
        call_command(
            "add_participant",
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )

    def test_add_participant(self):

        try:
            # TODO: Add user verification and create related competition
            self.call_command(email='test_user@codalab.org', competition=1, status="pending")
        except:
            # Competition 1 does not exist
            pass


class AddSubmissionCommand(TestCase):

    def call_command(self, *args, **kwargs):
        call_command(
            "add_submission",
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )

    def test_add_submission(self):

        try:
            # TODO: Create related competition and user. Submission should point to a submission file.
            self.call_command(email='test_user@codalab.org', competition=1, phase=None, submission=None)
        except:
            # Competition 1 does not exist
            pass
