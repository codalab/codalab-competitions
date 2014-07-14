import datetime
import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from apps.web import models

User = get_user_model()


class CompetitionEditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="organizer", password="pass")
        self.competition = models.Competition.objects.create(creator=self.user, modified_by=self.user)
        self.phase_1 = models.CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )
        self.dataset = models.OrganizerDataSet.objects.create(
            name="Test",
            type="None",
            data_file=SimpleUploadedFile("something.txt", "contents of file"),
            uploaded_by=self.user
        )
        self.client.login(username="organizer", password="pass")

    def test_edit_competition_adding_input_dataset_adds_to_model(self):
        # edit competition
        # add reference to Organizer data Set
        # save
        # verify references were created:
            # phase reference_data should point to the right thing
            # phase reference_data_organizer_dataset should point to the right thing



        # check that input points to NOTHING
        self.assertEquals(self.phase_1.input_data, None)


        resp = self.client.post(
            reverse("competitions:edit", kwargs={"pk":1}),
            {
                'phases-0-label': 'Phase 0 HPTdND',
                'phases-0-phasenumber': 0,
                'phases-MAX_NUM_FORMS': 1000,
                'pages-TOTAL_FORMS': 0,
                'image': '',
                'phases-0-DELETE': '',
                'phases-__prefix__-start_date': '',
                'phases-TOTAL_FORMS': 1,
                'phases-__prefix__-input_data_organizer_dataset': '',
                'phases-__prefix__-id': '',
                'has_registration': 'on',
                'phases-__prefix__-phasenumber': '',
                'phases-0-scoring_program_organizer_dataset': '',
                'phases-0-id': self.phase_1.pk,
                'title': 'Example Hello World Competition 06-24 24:41',
                'phases-__prefix__-scoring_program_organizer_dataset': '',
                'pages-__prefix__-id': '',
                'phases-__prefix__-leaderboard_management_mode': 'default',
                'phases-__prefix__-max_submissions': 100,
                'csrfmiddlewaretoken': 'ISaRrxAfjxeN8SYmV6e5NZgU7CjSoV50',
                'force_submission_to_leaderboard': 'on',
                'pages-__prefix__-label': '',
                'description': '<p>An example competition where submissions should output "Hello World!"</p>',
                'end_date': '',
                'phases-0-max_submissions': 100,
                'pages-__prefix__-html': '',
                'phases-0-input_data_organizer_dataset': self.dataset.pk,
                'phases-0-competition': self.competition.pk,
                'phases-0-start_date': '2014-06-24 15:41:24',
                'phases-0-leaderboard_management_mode': 'default',
                'phases-INITIAL_FORMS': 1,
                'phases-__prefix__-reference_data_organizer_dataset': '',
                'pages-INITIAL_FORMS': 4,
                'pages-__prefix__-competition': self.competition.pk,
                'phases-__prefix__-competition': self.competition.pk,
                'pages-MAX_NUM_FORMS': 1000,
                'phases-__prefix__-is_scoring_only': 'on',
                'phases-__prefix__-label': '',
                'phases-0-is_scoring_only': 'on',
                'pages-3-DELETE': '',
                'phases-0-reference_data_organizer_dataset': '',
            }
        )

        # Forwarded to competition detail page
        #self.assertEquals(resp.status_code, 302)

        # check that input points to something
        phase_updated = models.CompetitionPhase.objects.get(pk=self.phase_1.pk)
        self.assertEquals(phase_updated.input_data.file.name, self.dataset.data_file.file.name)

        #import ipdb; ipdb.set_trace()

        self.assertTrue(False)

    def test_edit_competition_adding_reference_dataset_adds_to_model(self):
        self.assertTrue(False)

    def test_edit_competition_adding_scoring_program_dataset_adds_to_model(self):
        self.assertTrue(False)
