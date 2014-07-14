import datetime
import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
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


class CompetitionEditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@user.com', username='testuser')
        self.other_user = User.objects.create(email='other@user.com', username='other')
        self.competition = Competition.objects.create(creator=self.user, modified_by=self.user)
        self.phase_1 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )


        # add organizer dataset here



    def test_edit_competition_adding_organizer_dataset_reference_adds_to_model(self):
        # edit competition
        # add reference to Organizer data Set
        # save
        # verify references were created:
            # phase reference_data should point to the right thing
            # phase reference_data_organizer_dataset should point to the right thing
            # dataset.competitions contains this competition now
        self.assertTrue(False)
