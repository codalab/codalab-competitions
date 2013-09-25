
"""
test for competition creation via api
"""
import sys, os.path, os, random, datetime
from django.utils import timezone
from django.core import management

# This is a really, really long way around saying that if the script is in
#  codalab\scripts\users.py, we need to add, ../../../codalab to the sys.path to find the settings
root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

# Import the configuration
from configurations import importer
importer.install()

from django.core.files import File
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.core import management

from apps.web.models import *

# Get the user model
User = get_user_model()

# Deal with time
current_time = timezone.now()
start_date = current_time - datetime.timedelta(days=1)

# Get a user to be the creator
guest1 = User.objects.get(username="guest1")


class CompetitionsPhase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@user.com',username='testuser')
        ParticipantStatus.objects.get_or_create(name='Pending',codename=ParticipantStatus.PENDING)
        self.test_data_path = settings.TEST_DATA_PATH
        management.call_command('create_competition', title='Test Title', description='Test Description',creator=self.user.email)
        self.competitions = [x.id for x in Competition.objects.all()]


    def create_base_competition(self):
        title = "Single-phase competition example"
        description = "This is an example of a single-phase competition."
        competition,created = Competition.objects.get_or_create(title=title, creator=guest1, modified_by=guest1, description=description)
        competition.save()
        return competition;
        
    #create a 3 phase test
    def test_three_phase_existance(self):
        competition = self.create_base_competition()

        # Phases for the competition
        day_delta = datetime.timedelta(days=30)
        phases = []
        for phase in [-1, 0, 1]:
            phase_start = start_date + (day_delta * phase)
            p, created = CompetitionPhase.objects.get_or_create(competition=competition, phasenumber=phase, label="Phase %d" % phase, start_date=phase_start, max_submissions=4)
            phases.append(p);
            
        self.assertEqual(len(phases), 3)


                         
    # create three phases, the middle phase should be active
    def test_three_phase_middle_active(self):
        competition = self.create_base_competition()

        # Phases for the competition
        day_delta = datetime.timedelta(days=30)
        phases = []
        for phase in [-1, 0, 1]:
            phase_start = start_date + (day_delta * phase)
            p, created = CompetitionPhase.objects.get_or_create(competition=competition, phasenumber=phase, label="Phase %d" % phase,
                                                            start_date=phase_start, max_submissions=4)
            phases.append(p);
            
        self.assertEqual(phases[0].is_active, False);
        self.assertEqual(phases[1].is_active, True);
        self.assertEqual(phases[2].is_active, False);


        
    # create two phases, the last phase should be active
    def test_two_phase_last_active(self):
        competition = self.create_base_competition()

        # Phases for the competition
        day_delta = datetime.timedelta(days = 30)
        phases = []
        for phase in [-1, 0]:  
            phase_start = start_date + (day_delta * phase)
            p, created = CompetitionPhase.objects.get_or_create(competition=competition, phasenumber=phase, label="Phase %d" % phase,
                                                            start_date=phase_start, max_submissions=4)
            phases.append(p);
            print phase_start

        self.assertEqual(phases[0].is_active, False);
        self.assertEqual(phases[1].is_active, True);
 
