
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
from django.core import mail
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

class ParticipationStatusEmailTests(TestCase):

    def _participant_join_competition(self, cleanup_email=False):
        self.client.login(username="participant", password="pass")
        resp = self.client.post(reverse('competition-participate', kwargs={'pk': self.competition.pk}))
        self.client.logout()

        if cleanup_email:
            mail.outbox = []

        return resp

    def setUp(self):
        statuses = ['unknown', 'denied', 'approved', 'pending']
        for s in statuses:
            ParticipantStatus.objects.get_or_create(name=s, codename=s)

        self.organizer_user = User.objects.create_user(username="organizer", password="pass")
        self.participant_user = User.objects.create_user(username="participant", password="pass")
        self.competition = Competition.objects.create(
            title="Test Competition",
            creator=self.organizer_user,
            modified_by=self.organizer_user
        )

    def test_attempting_to_join_competition_sends_emails(self):
        # Require approval
        self.competition.has_registration = True
        self.competition.save()

        resp = self._participant_join_competition()

        self.assertEquals(resp.status_code, 200)

        subjects = [m.subject for m in mail.outbox]
        self.assertIn('Application to Test Competition sent', subjects)
        self.assertIn('%s applied to your competition' % self.participant_user, subjects)

    def test_participation_update_emails_contain_valid_links(self):
        self._participant_join_competition()

        for m in mail.outbox:
            self.assertIn("http://example.com/my/settings", m.body)
            self.assertIn("http://example.com/competitions/%s" % self.competition.pk, m.body)

    def test_attempting_to_join_competition_auto_approved_sends_emails(self):
        resp = self._participant_join_competition()

        self.assertEquals(resp.status_code, 200)

        subjects = [m.subject for m in mail.outbox]
        self.assertIn('Accepted into Test Competition!', subjects)
        self.assertIn('%s accepted into your competition!' % self.participant_user, subjects)

    def test_attempting_to_join_competition_not_logged_in_doesnt_send_email(self):
        resp = self.client.post(reverse('competition-participate', kwargs={'pk': self.competition.pk}))

        self.assertEquals(resp.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)

    def test_participation_status_update_approved_sends_email(self):
        self._participant_join_competition(cleanup_email=True)

        participant = CompetitionParticipant.objects.get(competition=self.competition, user=self.participant_user)

        self.client.login(username="organizer", password="pass")
        resp = self.client.post(
            reverse('competition-participation-status', kwargs={'pk': self.competition.pk}),
            {
                "status": "approved",
                "participant_id": participant.pk,
                "reason": ""
            }
        )

        self.assertEquals(resp.status_code, 200)

        subjects = [m.subject for m in mail.outbox]
        self.assertIn('Accepted into %s!' % self.competition, subjects)
        self.assertIn('%s accepted into your competition!' % self.participant_user, subjects)

    def test_participation_status_update_revoked_sends_email(self):
        self._participant_join_competition(cleanup_email=True)

        participant = CompetitionParticipant.objects.get(competition=self.competition, user=self.participant_user)

        self.client.login(username="organizer", password="pass")
        resp = self.client.post(
            reverse('competition-participation-status', kwargs={'pk': self.competition.pk}),
            {
                "status": "denied",
                "participant_id": participant.pk,
                "reason": ""
            }
        )

        self.assertEquals(resp.status_code, 200)

        subjects = [m.subject for m in mail.outbox]
        self.assertIn('Permission revoked from Test Competition!', subjects)
        self.assertIn("%s's permission revoked from your competition!" % self.participant_user, subjects)

    def test_participation_status_update_not_sent_when_participant_disables_status_notifications(self):
        self.participant_user.participation_status_updates = False
        self.participant_user.save()

        self._participant_join_competition()

        self.assertEqual(len(mail.outbox), 1)

    def test_organizer_not_notified_participant_joining_competition_if_opted_out(self):
        self.organizer_user.organizer_status_updates = False
        self.organizer_user.save()

        self._participant_join_competition()

        self.assertEqual(len(mail.outbox), 1)


class ParticipationStatusPermissionsTests(TestCase):

    def setUp(self):
        statuses = ['unknown', 'denied', 'approved', 'pending']
        for s in statuses:
            ParticipantStatus.objects.get_or_create(name=s, codename=s)

        self.organizer_user = User.objects.create_user(username="organizer", password="pass")
        self.participant_user = User.objects.create_user(username="participant", password="pass")
        self.competition = Competition.objects.create(
            title="Test Competition",
            creator=self.organizer_user,
            modified_by=self.organizer_user
        )
        self.participant = CompetitionParticipant.objects.create(
            user=self.participant_user,
            competition=self.competition,
            status=ParticipantStatus.objects.get(codename=ParticipantStatus.PENDING)
        )

    def test_updating_participant_status_denied_without_competition_ownership(self):
        self.client.login(username="participant", password="pass")
        resp = self.client.post(
            reverse('competition-participation-status', kwargs={'pk': self.competition.pk}),
            {
                "status": ParticipantStatus.APPROVED,
                "participant_id": self.participant.pk,
                "reason": ""
            }
        )

        self.assertEquals(resp.status_code, 403)

    def test_updating_participant_status_works_as_owner(self):
        self.client.login(username="organizer", password="pass")
        resp = self.client.post(
            reverse('competition-participation-status', kwargs={'pk': self.competition.pk}),
            {
                "status": ParticipantStatus.APPROVED,
                "participant_id": self.participant.pk,
                "reason": ""
            }
        )

        self.assertEquals(resp.status_code, 200)

        participant_with_new_status = CompetitionParticipant.objects.get(pk=self.participant.pk)

        self.assertEquals(participant_with_new_status.status.codename, ParticipantStatus.APPROVED)
