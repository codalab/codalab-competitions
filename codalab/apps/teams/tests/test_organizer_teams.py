import datetime

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils.timezone import now

from apps.web.models import Competition, CompetitionParticipant, CompetitionPhase, ParticipantStatus

User = get_user_model()


class CompetitionPhaseToPhase(TestCase):
    def setUp(self):
        self.creator = User.objects.create(email='test@user.com', username='testuser')
        self.creator.set_password('test')
        self.creator.save()

        self.admin = User.objects.create(email='testadmin@user.com', username='testadminuser')
        self.admin.set_password('testadmin')
        self.admin.save()

        self.user = User.objects.create(email='testclient@user.com', username='testclientuser')
        self.user.set_password('testclient')
        self.user.save()

        self.competition = Competition.objects.create(creator=self.creator, modified_by=self.creator)
        self.competition.admins.add(self.admin)
        self.competition.save()

    def test_who_can_create_organizer_teams(self):
        creator = Client()
        creator.login(username='testuser', password='test')
        resp = creator.post(reverse('create_org_team', kwargs={'competition_pk': self.competition.pk}), {"text_members": "test@user.com", "name": "Test Team 1", "description": "Test Team"})
        assert(resp.status_code == 302)

        user = Client()
        user.login(username='testclientuser', password='testclient')
        resp = user.post(reverse('create_org_team', kwargs={'competition_pk': self.competition.pk}),
                      {"text_members": "testclient@user.com", "name": "Test Team 2", "description": "Test Team"})
        assert (resp.status_code == 403)

        admin = Client()
        admin.login(username='testadminuser', password='testadmin')
        resp = admin.post(reverse('create_org_team', kwargs={'competition_pk': self.competition.pk}),
                         {"text_members": "testadmin@user.com", "name": "Test Team 3", "description": "Test Team"})
        assert (resp.status_code == 302)

        anon = Client()
        # admin.login(username='testadminuser', password='testadmin')
        resp = anon.post(reverse('create_org_team', kwargs={'competition_pk': self.competition.pk}),
                         {"text_members": "testadmin@user.com", "name": "Test Team 4", "description": "Test Team"})
        assert (resp.url == 'http://testserver/accounts/login/?next=/teams/1/create_org_team/')
