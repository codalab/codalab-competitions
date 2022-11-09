from django.test import TestCase, RequestFactory

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse
from django.utils.timezone import now, timedelta, datetime

from apps.web import views, models


class HomePageTest(TestCase):
    def test_context_not_single_competition_view(self):
        with self.settings(SINGLE_COMPETITION_VIEW_PK=None):
            try:
                request = RequestFactory().get('/')

                response = views.HomePageView.as_view()(request)

                self.assertIn('latest_competitions', response.context_data)
            except models.Competition.DoesNotExist:
                # Competition does not exist. Create competition to test content
                pass

    def test_context_single_competition_view(self):
        try:
            request = RequestFactory().get('/')

            response = views.HomePageView.as_view()(request)

            self.assertIn('latest_competitions', response.context_data)
        except Exception:
            # Competition does not exist. Create competition to test content
            pass


class MyAdminTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test_user@codalab.org', password='secret_password')

    def test_with_anonymous_user(self):
        request = self.factory.get(reverse('admin_monitoring_links'))
        request.user = AnonymousUser()
        response = views.MyAdminView.as_view()(request)

        self.assertEqual(response.status_code, 302)

    def test_with_no_admin_user(self):
        request = self.factory.get(reverse('admin_monitoring_links'))
        request.user = self.user
        request.user.is_staff = False
        request.user.save()
        request.user = self.user
        response = views.MyAdminView.as_view()(request)

        self.assertEqual(response.status_code, 302)

    def test_with_admin_user(self):
        request = self.factory.get(reverse('admin_monitoring_links'))
        request.user = self.user
        request.user.is_staff = True
        request.user.save()
        response = views.MyAdminView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('domain', response.context_data)
        self.assertIn('rabbit_port', response.context_data)
        self.assertIn('flower_port', response.context_data)


class HighlightsTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_view(self):
        request = self.factory.get(reverse('highlights'))
        response = views.Highlights.as_view()(request)

        self.assertEqual(response.status_code, 200)

        self.assertIn('general_stats', response.context_data)


class UserDetailTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test_user@codalab.org', password='secret_password')

    def test_view(self):
        request = self.factory.get(reverse('user_details', kwargs={'pk': self.user.pk}))
        request.user = self.user
        response = views.UserDetailView.as_view()(request, pk=self.user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertIn('information', response.context_data)


class CompetitionSubmissionViewsTest(TestCase):
    """
        Test different views related with competition data
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create(email='test@user.com', username='testuser')
        self.other_user = get_user_model().objects.create(email='other@user.com', username='other')
        self.customizer_configuration = models.Configuration.objects.create(disable_all_submissions=False)
        self.competition = models.Competition.objects.create(creator=self.user, modified_by=self.user)
        self.participant_1 = models.CompetitionParticipant.objects.create(
            user=self.user,
            competition=self.competition,
            status=models.ParticipantStatus.objects.get_or_create(
                name='approved', codename=models.ParticipantStatus.APPROVED
            )[0]
        )
        self.participant_2 = models.CompetitionParticipant.objects.create(
            user=self.other_user,
            competition=self.competition,
            status=models.ParticipantStatus.objects.get_or_create(
                name='approved', codename=models.ParticipantStatus.APPROVED
            )[0]
        )
        self.phase_1 = models.CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=now() - timedelta(days=30),
        )
        self.phase_2 = models.CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=2,
            start_date=now() - timedelta(days=15),
            auto_migration=True
        )

        submission_finished = models.CompetitionSubmissionStatus.objects.create(
            name="finished", codename="finished"
        )

        self.submission_1 = models.CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=now() - timedelta(days=29)
        )
        self.submission_2 = models.CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=now() - timedelta(days=28)
        )

        self.submission_3 = models.CompetitionSubmission.objects.create(
            participant=self.participant_2,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=now() - timedelta(days=28)
        )

        self.leader_board = models.PhaseLeaderBoard.objects.create(phase=self.phase_1)
        self.leader_board_entry_1 = models.PhaseLeaderBoardEntry.objects.create(
            board=self.leader_board,
            result=self.submission_2
        )
        self.leader_board_entry_2 = models.PhaseLeaderBoardEntry.objects.create(
            board=self.leader_board,
            result=self.submission_3
        )

    def test_competition_submissions_page(self):
        request = self.factory.get(reverse('competitions:competition_submissions_page',
                                           kwargs={
                                               'id': self.competition.id,
                                               'phase': self.phase_1.id,
                                           }))
        request.user = self.participant_1.user
        response = views.CompetitionSubmissionsPage.as_view()(
            request, id=self.competition.id, phase=self.phase_1.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('phase', response.context_data)
        self.assertIn('submission_info_list', response.context_data)

    def test_competition_results_page(self):
        request = self.factory.get(reverse('competitions:competition_results_page',
                                           kwargs={
                                               'id': self.competition.id,
                                               'phase': self.phase_1.id,
                                           }))
        request.user = self.participant_1.user
        response = views.CompetitionResultsPage.as_view()(
            request, id=self.competition.id, phase=self.phase_1.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('phase', response.context_data)
        self.assertIn('is_owner', response.context_data)
        self.assertIn('groups', response.context_data)
        self.assertIn('competition_admins', response.context_data)

    def test_competition_public_submission_page(self):
        request = self.factory.get(reverse('competitions:public_submissions',
                                           kwargs={
                                               'pk': self.competition.id,
                                           }))
        request.user = self.participant_1.user
        response = views.CompetitionPublicSubmission.as_view()(
            request, pk=self.competition.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('active_phase', response.context_data)
        self.assertIn('competition', response.context_data)

    def test_competition_public_submission_by_phases_page(self):
        request = self.factory.get(reverse('competitions:public_submissions_phase',
                                           kwargs={
                                               'pk': self.competition.id,
                                               'phase': self.phase_1.id,
                                           }))
        request.user = self.participant_1.user
        response = views.CompetitionPublicSubmissionByPhases.as_view()(
            request, pk=self.competition.id, phase=self.phase_1.id,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('public_submissions', response.context_data)
        self.assertIn('competition', response.context_data)

    def test_competition_results_download(self):
        request = self.factory.get(reverse('competitions:competition_results_download',
                                           kwargs={
                                               'id': self.competition.id,
                                               'phase': self.phase_1.id,
                                           }))
        request.user = self.participant_1.user
        response = views.CompetitionResultsDownload.as_view()(
            request, id=self.competition.id, phase=self.phase_1.id,
        )

        self.assertEqual(response.status_code, 200)
