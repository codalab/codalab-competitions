# -*- coding: cp1252 -*-
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

        
        
    def test_get_competition_api(self):
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
        data = json.loads(res.content)
        
        #get competition id
        res = client.get('/api/competition/'+ str(data['id'])+'/')
        data = json.loads(res.content)
        self.assertEqual(data['title'], 'Test Title')
        self.assertEqual(data['description'], 'Description')
        self.assertEqual(data['creator'], self.user.pk)
        self.assertEqual(data['modified_by'], self.user.pk)


        
    def test_delete_competition_api(self):
       
        client = Client()
        
        #create a competition                                         
        res = client.post('/api/competition/', {'title': 'Test Title',
                                                 'description': 'Description',
                                                 'creator': self.user.pk,
                                                 'modified_by': self.user.pk,
                                                 })
        create_data = json.loads(res.content)

        #delete a competition
        res = client.delete('/api/competition/'+ str(create_data['id'])+'/')
        delete_data = json.loads(res.content)

        #try to access the deleted comp
        res = client.get('/api/competition/'+ delete_data + '/')
        self.assertEqual(int(res.status_code), int(404))

        

    def test_delete_one_from_two_competitions_api(self):
       
        client = Client()
        
        #create a competition                                         
        res = client.post('/api/competition/', {'title': 'Test Title 1',
                                                 'description': 'Description',
                                                 'creator': self.user.pk,
                                                 'modified_by': self.user.pk,
                                                 })      
        create_data1 = json.loads(res.content)

        
        #create another
        res = client.post('/api/competition/', {'title': 'Test Title 2',
                                                 'description': 'Description',
                                                 'creator': self.user.pk,
                                                 'modified_by': self.user.pk,
                                                 })
        
        create_data2 = json.loads(res.content)
        
        
        #delete  first competition
        res = client.delete('/api/competition/'+ str(create_data1['id'])+'/')
        delete_data = json.loads(res.content)
        
        
        #try to access the deleted comp
        res = client.get('/api/competition/'+ str(create_data1['id'])+'/')      
        self.assertEqual(int(res.status_code), int(404))   
