import datetime
import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model

from apps.web.models import (Competition,
                             CompetitionParticipant,
                             CompetitionPhase,
                             CompetitionSubmission,
                             CompetitionSubmissionStatus,
                             ParticipantStatus,
                             PhaseLeaderBoard,
                             PhaseLeaderBoardEntry)

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
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )
        self.phase_2 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=2,
            start_date=datetime.datetime.now() - datetime.timedelta(days=15),
            auto_migration=True
        )

        submission_finished = CompetitionSubmissionStatus.objects.create(name="finished", codename="finished")

        self.submission_1 = CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=29)
        )
        self.submission_2 = CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=28)
        )

        self.submission_3 = CompetitionSubmission.objects.create(
            participant=self.participant_2,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=28)
        )

        self.leader_board = PhaseLeaderBoard.objects.create(phase=self.phase_1)
        self.leader_board_entry_1 = PhaseLeaderBoardEntry.objects.create(
            board=self.leader_board,
            result=self.submission_2
        )
        self.leader_board_entry_2 = PhaseLeaderBoardEntry.objects.create(
            board=self.leader_board,
            result=self.submission_3
        )

        self.client = Client()

    def test_scheduler_url_calls_competition_phase_migration_check(self):
        with mock.patch('apps.web.models.Competition.check_trailing_phase_submissions') as check_trailing_mock:
            resp = self.client.get('/competitions/check_phase_migrations')

        self.assertTrue(check_trailing_mock.called)

    def test_check_trailing_phase_submissions_doesnt_trigger_migrations_if_they_are_done(self):
        with mock.patch('apps.web.models.Competition.do_phase_migration') as do_migration_mock:
            competition_doesnt_need_migrated = Competition.objects.create(creator=self.user, modified_by=self.user)
            only_phase = CompetitionPhase.objects.create(
                competition=competition_doesnt_need_migrated,
                phasenumber=1,
                start_date=datetime.datetime.now() - datetime.timedelta(days=30)
            )

            competition_doesnt_need_migrated.check_trailing_phase_submissions()

        self.assertFalse(do_migration_mock.called)

    def test_check_trailing_phase_submissions_triggered_if_migrations_have_not_been_done(self):
        with mock.patch('apps.web.models.Competition.do_phase_migration') as do_migration_mock:
            self.competition.check_trailing_phase_submissions()

        self.assertTrue(do_migration_mock.called)

    def test_check_trailing_phase_submissions_migrates_trailing_submissions_properly(self):
        with mock.patch('apps.web.tasks.evaluate_submission') as evaluate_mock:
            self.competition.check_trailing_phase_submissions()

        self.assertTrue(evaluate_mock.called)

        self.assertEquals(self.submission_1.phase, self.phase_1)
        self.assertEquals(self.submission_2.phase, self.phase_1)
        self.assertEquals(self.submission_3.phase, self.phase_1)

        CompetitionSubmission.objects.get(phase=self.phase_2, participant=self.participant_1)
        CompetitionSubmission.objects.get(phase=self.phase_2, participant=self.participant_2)

        self.assertEquals(self.competition.last_phase_migration, 2)

    def test_phase_to_phase_migrations_only_when_auto_migration_flag_is_true(self):
        with mock.patch('apps.web.models.Competition.do_phase_migration') as do_migration_mock:
            competition = Competition.objects.create(creator=self.user, modified_by=self.user)
            first_phase = CompetitionPhase.objects.create(
                competition=competition,
                phasenumber=1,
                start_date=datetime.datetime.now() - datetime.timedelta(days=30)
            )
            second_phase = CompetitionPhase.objects.create(
                competition=competition,
                phasenumber=2,
                start_date=datetime.datetime.now() - datetime.timedelta(days=20),
                auto_migration=False
            )

            competition.check_trailing_phase_submissions()

        self.assertFalse(do_migration_mock.called)

    def test_phase_migrations_not_ran_concurrently_while_is_migrating_is_true(self):
        with mock.patch('apps.web.models.Competition.do_phase_migration') as do_migration_mock:
            # While is_migrating is true, do_migration should never be called
            self.competition.is_migrating = True
            self.competition.save()

            self.competition.check_trailing_phase_submissions()

        self.assertFalse(do_migration_mock.called)


class CompetitionTest(TestCase):

    def setUp(self):
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
            status=ParticipantStatus.objects.get_or_create(name='approved', codename=ParticipantStatus.PENDING)[0]
        )


class CompetitionDeleteTests(CompetitionTest):

    def test_cant_view_delete_competition_template_if_you_dont_own_it(self):
        self.client.login(username="participant", password="pass")
        resp = self.client.get(reverse("competitions:delete", kwargs={"pk": self.competition.pk}))

        self.assertEquals(resp.status_code, 403)

    def test_can_view_competition_with_ownership(self):
        self.client.login(username="organizer", password="pass")
        resp = self.client.get(reverse("competitions:delete", kwargs={"pk": self.competition.pk}))

        self.assertEquals(resp.status_code, 200)

    def test_cant_delete_competition_if_you_dont_own_it(self):
        self.client.login(username="participant", password="pass")
        resp = self.client.delete(reverse("competitions:delete", kwargs={"pk": self.competition.pk}))

        self.assertEquals(resp.status_code, 403)

    def test_can_delete_competition_with_ownership(self):
        self.client.login(username="organizer", password="pass")
        resp = self.client.delete(reverse("competitions:delete", kwargs={"pk": self.competition.pk}))

        self.assertEquals(resp.status_code, 302)
        self.assertEquals(len(Competition.objects.filter(pk=self.competition.pk)), 0)


class CompetitionEditPermissionsTests(CompetitionTest):

    def test_cant_view_edit_competition_template_if_you_dont_own_it(self):
        self.client.login(username="participant", password="pass")
        resp = self.client.get(reverse("competitions:edit", kwargs={"pk": self.competition.pk}))

        self.assertEquals(resp.status_code, 403)

    def test_can_view_edit_competition_with_ownership(self):
        self.client.login(username="organizer", password="pass")
        resp = self.client.get(reverse("competitions:edit", kwargs={"pk": self.competition.pk}))

        self.assertEquals(resp.status_code, 200)

    def test_cant_edit_competition_if_you_dont_own_it(self):
        self.client.login(username="participant", password="pass")
        resp = self.client.post(reverse("competitions:edit", kwargs={"pk": self.competition.pk}))

        self.assertEquals(resp.status_code, 403)

    def test_can_edit_competition_with_ownership(self):
        self.client.login(username="organizer", password="pass")
        with mock.patch('apps.web.views.CompetitionEdit.construct_inlines') as construct_inlines_mock:
            resp = self.client.post(
                reverse("competitions:edit", kwargs={"pk": self.competition.pk}),
                data={}
            )

        self.assertTrue(construct_inlines_mock.called)
