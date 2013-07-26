"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core import management
from django.test import TestCase
from apps.authenz.models import User
from apps.web.models import Competition,ParticipantStatus,CompetitionParticipant


class SimpleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@user.com',username='testuser')
        ParticipantStatus.objects.get_or_create(name='Pending',codename='pending')
        
        management.call_command('create_competition', title='Test Title', description='Test Description',creator=self.user.email)
        self.competitions = [x.id for x in Competition.objects.all()]

    def test_add_participant(self):
        """
        Adds a participant with a management command
        """
        management.call_command('add_participant', email='user1@test.com', competition=self.competitions[0])
        p = CompetitionParticipant.objects.get(user__email='user1@test.com',competition_id=self.competitions[0])
        assert(p.competition_id == self.competitions[0])
