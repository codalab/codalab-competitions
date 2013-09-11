"""
Tests for Codalab functionality.
"""
import os
import json

from django.conf import settings
from django.core import management
from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test.client import Client

from django.contrib.auth import get_user_model

from apps.web.models import Competition, ParticipantStatus, CompetitionParticipant

User =  get_user_model()

class Competitions(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@user.com',username='testuser')
        ParticipantStatus.objects.get_or_create(name='Pending',codename=ParticipantStatus.PENDING)
        self.test_data_path = settings.TEST_DATA_PATH
        management.call_command('create_competition', title='Test Title', description='Test Description',creator=self.user.email)
        self.competitions = [x.id for x in Competition.objects.all()]

    def test_add_participant(self):
        """
        Add a participant to a competition.
        """
        management.call_command('add_participant', email='user1@test.com', competition=self.competitions[0])
        p = CompetitionParticipant.objects.get(user__email='user1@test.com',competition_id=self.competitions[0])
        assert(p.competition_id == self.competitions[0])

    def test_create_competition_api(self):
        """
        Create a competition programmatically.
        TODO: Does not authenticate (YET) 
        """
        client = Client()
        res = client.post('/api/competition/', {'title': 'Test Title',
                                                 'description': 'Description',
                                                 'creator': self.user.pk,
                                                 'modified_by': self.user.pk,
                                                 })
        # Status 201: Created
        self.assertEqual(int(res.status_code),int(201))
        data = json.loads(res.content)
        
        # Just checking to make sure the data was returned correctly
        self.assertTrue('id' in data and data['id'] >= 1)
    
    
