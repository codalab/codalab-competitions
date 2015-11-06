import datetime
import mock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.client import Client

from apps.web.models import (Competition,
                             CompetitionParticipant,
                             CompetitionPhase,
                             CompetitionSubmission,
                             CompetitionSubmissionStatus,
                             ParticipantStatus,
                             PhaseLeaderBoard,
                             PhaseLeaderBoardEntry)

User = get_user_model()


class CompetitionHiddenPhaseMigration(TestCase):
    def setUp(self):
        '''
	    Test to check for migratiosn
	    1. Create user
	    2. User becomes the competition's
	    3. add participants to the competition
	    4. created two phases
	    5. Created a submission status
	    6. Make some submissions
	    7. Create a leaderboard for phase number 1
	    8. Create to leaderboard entries

	    Funtions:
	    1.
        '''

        self.user = User.objects.create(email='test@user.com', username='testuser')
        self.other_user = User.objects.create(email='other@user.com', username='other')
        self.third_user = User.objects.create(email='third@user.com', username="third")
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
        self.participant_3 = CompetitionParticipant.objects.create(
            user=self.third_user,
            competition=self.competition,
            status=ParticipantStatus.objects.get_or_create(name="approved", codename=ParticipantStatus.APPROVED)[0]
        )
        self.phase_1 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=1,
            start_date=datetime.datetime.now() - datetime.timedelta(days=30),
        )
        self.phase_2 = CompetitionPhase.objects.create(
            competition=self.competition,
            phasenumber=2,
            start_date=datetime.datetime.now() + datetime.timedelta(days=15),
            auto_migration=True
        )

        submission_finished = CompetitionSubmissionStatus.objects.create(name="finished", codename="finished")

        self.submission_1 = CompetitionSubmission.objects.create(
            participant=self.participant_1,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=29),
            is_migrated=False
        )
        self.submission_2 = CompetitionSubmission.objects.create(
            participant=self.participant_2,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=28)
        )

        self.submission_3 = CompetitionSubmission.objects.create(
            participant=self.participant_3,
            phase=self.phase_1,
            status=submission_finished,
            submitted_at=datetime.datetime.now() - datetime.timedelta(days=27)
        )

        self.leader_board = PhaseLeaderBoard.objects.create(phase=self.phase_1)
        self.leader_board_entry_1 = PhaseLeaderBoardEntry.objects.create(
            board=self.leader_board,
            result=self.submission_1
        )
        self.leader_board_entry_1 = PhaseLeaderBoardEntry.objects.create(
            board=self.leader_board,
            result=self.submission_2
        )
        self.leader_board_entry_2 = PhaseLeaderBoardEntry.objects.create(
            board=self.leader_board,
            result=self.submission_3
        )

        self.client = Client()

    def test_scheduler_url_call_competition_phase_migration(self):
        with mock.patch('apps.web.models.Competition.check_future_phase_sumbmissions') as check_future_migrations_mock:
            resp = self.client.get('/competitions/check_phase_migrations')

        self.assertTrue(check_future_migrations_mock.called)

    def test_phase_to_phase_migrations_only_when_auto_migration_flag_is_true(self):
        '''
        Will only migrate when phase 2 auto_migration = True
        '''
        with mock.patch('apps.web.models.Competition.apply_phase_migration') as do_migration_mock:
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

            competition.check_future_phase_sumbmissions()

        self.assertFalse(do_migration_mock.called)

    def test_perform_migration_when_flag_is_true(self):
        '''
        Will perform a migrationg when auto_migration = True
        '''
        with mock.patch('apps.web.models.Competition.apply_phase_migration') as do_migration_mock:
            competition = Competition.objects.create(creator=self.user, modified_by=self.user)
            first_phase = CompetitionPhase.objects.create(
                competition=competition,
                phasenumber=1,
                start_date=datetime.datetime.now() - datetime.timedelta(days=30)
                )
            second_phase = CompetitionPhase.objects.create(
                competition=competition,
                phasenumber=2,
                start_date=datetime.datetime.now() + datetime.timedelta(days=20),
                auto_migration=True
                )
            competition.check_future_phase_sumbmissions()

        self.assertTrue(do_migration_mock.called)

    def test_perform_migration_when_submission_flag_is_False(self):
        '''
        Will perform migrations when submission auto_migrated = False
        1. We need a few submissions to test this behavior
        '''
        with mock.patch('apps.web.tasks.evaluate_submission') as perform_migration:
            self.submission_1.is_migrated = False
            self.submission_2.is_migrated = False
            self.submission_1.save()
            self.submission_2.save()
            self.competition.check_future_phase_sumbmissions()

        self.assertTrue(perform_migration.called)

    def test_phase_migrations_not_ran_concurrently_while_is_migrating_is_true(self):
        with mock.patch('apps.web.models.Competition.apply_phase_migration') as do_migration_mock:
            # While is_migrating is true, do_migration should never be called
            self.competition.is_migrating = True
            self.competition.save()

            self.competition.check_future_phase_sumbmissions()

        self.assertFalse(do_migration_mock.called)

    def test_phase_migrations_delayed_until_submissions_not_marked_running(self):
        self.submission_1.status = CompetitionSubmissionStatus.objects.get_or_create(name="running", codename="running")[0]
        self.submission_1.save()

        with mock.patch('apps.web.tasks.evaluate_submission') as evaluate_mock:
            self.competition.check_future_phase_sumbmissions()
        self.assertFalse(evaluate_mock.called)

        self.submission_1.status = CompetitionSubmissionStatus.objects.get_or_create(name="finished", codename="finished")[0]
        self.submission_1.is_migrated = False
        self.submission_1.save()
        with mock.patch('apps.web.tasks.evaluate_submission') as evaluate_mock:
            self.competition.check_future_phase_sumbmissions()
        self.assertTrue(evaluate_mock.called)

    def test_phase_migrations_delayed_marks_competition(self):
        self.submission_1.status = CompetitionSubmissionStatus.objects.get_or_create(name="running", codename="running")[0]
        self.submission_1.save()
        self.assertFalse(self.competition.is_migrating_delayed)

        with mock.patch('apps.web.tasks.evaluate_submission') as evaluate_mock:
            self.competition.check_future_phase_sumbmissions()
        self.assertTrue(self.competition.is_migrating_delayed)

    def test_submissions_marked_as_migrated(self):
        self.submission_1.status = CompetitionSubmissionStatus.objects.get_or_create(name="finished", codename="finished")[0]
        self.submission_2.status = CompetitionSubmissionStatus.objects.get_or_create(name="finished", codename="finished")[0]
        self.submission_1.save()
        self.submission_2.save()
        self.assertFalse(self.submission_1.is_migrated)
        self.assertFalse(self.submission_2.is_migrated)
