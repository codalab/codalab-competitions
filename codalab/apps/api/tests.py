
"""
test for competition creation via api
"""
import sys
import os.path
import os
import datetime
from django.utils import timezone

# This is a really, really long way around saying that if the script is in
# codalab\scripts\users.py, we need to add, ../../../codalab to the
# sys.path to find the settings
root_dir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

# Import the configuration
from configurations import importer
importer.install()

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.web.models import *

# Get the user model
User = get_user_model()

# Deal with time
current_time = timezone.now()
start_date = current_time - datetime.timedelta(days=1)


class CompetitionsPhase(TestCase):

    def setUp(self):
        # Get a user to be the creator
        self.guest1 = User.objects.create(username="apiguest1")

    def create_base_competition(self):
        title = "Single-phase competition example"
        description = "This is an example of a single-phase competition."
        competition, created = Competition.objects.get_or_create(
            title=title, creator=self.guest1, modified_by=self.guest1, description=description)
        return competition

    # Create a 3 phase test
    def test_three_phase_existance(self):
        competition = self.create_base_competition()

        # Phases for the competition
        day_delta = datetime.timedelta(days=30)
        phases = []
        for phase in [1, 2, 3]:
            phase_start = start_date + (day_delta * (phase - 2))
            p, created = CompetitionPhase.objects.get_or_create(
                competition=competition, phasenumber=phase, label="Phase %d" % phase, start_date=phase_start, max_submissions=4)
            phases.append(p)

        self.assertEqual(len(phases), 3)

    # Create three phases, the middle phase should be active
    def test_three_phase_middle_active(self):
        competition = self.create_base_competition()

        # Phases for the competition
        day_delta = datetime.timedelta(days=30)
        phases = []
        for phase in [1, 2, 3]:
            phase_start = start_date + (day_delta * (phase - 2))
            p, created = CompetitionPhase.objects.get_or_create(
                competition=competition, phasenumber=phase, label="Phase %d" % phase,
                start_date=phase_start, max_submissions=4)
            phases.append(p)

        self.assertEqual(phases[0].is_active, False)
        self.assertEqual(phases[1].is_active, True)
        self.assertEqual(phases[2].is_active, False)

    # Create two phases, the last phase should be active
    def test_two_phase_last_active(self):
        competition = self.create_base_competition()

        # Phases for the competition
        day_delta = datetime.timedelta(days=30)
        phases = []
        for phase in [1, 2]:
            phase_start = start_date + (day_delta * (phase - 2))
            p, created = CompetitionPhase.objects.get_or_create(
                competition=competition, phasenumber=phase, label="Phase %d" % phase,
                start_date=phase_start, max_submissions=4)
            phases.append(p)
            print phase_start

        self.assertEqual(phases[0].is_active, False)
        self.assertEqual(phases[1].is_active, True)

# Publish / Unpublish Test
# Create a competition
# Get the list of competitions (The new one should not be in it, and the new one should have the published flag set to false)
# Publish the new one
# The new one should be in the list and have the published flag set to true
# Check turning off works

class ParticipationStatusEmails(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="organizer")
        self.other_user = User.objects.create(username="participant")
        self.competition = Competition.objects.create(creator=self.user)

    def test_attempting_to_join_competition_emails(self):
        # try to join competition
        # was an email sent?

        self.client.get()
        pass

    def test_participation_status_update_sends_email(self):
        # make participant with status = pending
        # approve status
        # is email sent?
        pass

    pass
