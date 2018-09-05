import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from apps.web.models import Competition, CompetitionParticipant, CompetitionPhase, ParticipantStatus

User = get_user_model()


class CompetitionPhaseToPhase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@user.com', username='testuser')
        self.other_user = User.objects.create(email='other@user.com', username='other')
        self.competition = Competition.objects.create(creator=self.user, modified_by=self.user)
        self.participant_1 = CompetitionParticipant.objects.create(
            user=self.user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.participant_2 = CompetitionParticipant.objects.create(
            user=self.other_user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.APPROVED)[0]
        )
        self.phase_1 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=now() - datetime.timedelta(days=30),
        )
        self.phase_2 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=2,
            start_date=now() - datetime.timedelta(days=15),
        )

    def test_chahub_data_includes_proper_phase_end_dates(self):
        chahub_data = self.competition.get_chahub_data()

        # End dates for phases to chahub automatically are set to -1 minute from next phase end date
        phase_end_date = self.phase_2.start_date - datetime.timedelta(minutes=1)
        
        assert chahub_data[0]['phases'][0]['end'] == phase_end_date.isoformat()
        assert chahub_data[0]['phases'][1]['end'] is None  # never ends
