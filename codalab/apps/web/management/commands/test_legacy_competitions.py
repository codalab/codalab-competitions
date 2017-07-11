import json

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.web.models import CompetitionSubmission, CompetitionSubmissionStatus
from apps.web.tasks import evaluate_submission


class Command(BaseCommand):
    help = """
    Gets one successful submission from each competition, runs it, and saves each new
    submission to `codalab/test_submissions.csv` where we can then iterate through and look at
    the status of each submission.
    """

    def handle(self, *args, **options):
        try:
            submission_dump = json.loads(open("test_submissions.json", "r+").read())
        except (IOError, ValueError):
            submission_dump = None

        print(submission_dump)

        if submission_dump:
            completed_submissions = CompetitionSubmission.objects.filter(
                pk__in=submission_dump.keys(),
                status__codename__in=('finished', 'failed')
            ).select_related('status', 'phase', 'phase__competition')
            for s in completed_submissions:
                submission_dump[str(s.pk)]= {
                    "status": s.status.codename,
                    "competition": s.phase.competition.pk
                }
            open("test_submissions.json", "w+").write(json.dumps(submission_dump))
        else:
            submission_dump = {}
            submissions = CompetitionSubmission.objects.filter(
                status__codename=CompetitionSubmissionStatus.FINISHED
            ).distinct('phase__competition').select_related('phase')

            for s in submissions:
                if settings.USE_AWS:
                    file_kwarg = {'s3_file': s.s3_file}
                else:
                    file_kwarg = {'file': s.file}

                new_submission = CompetitionSubmission(
                    participant=s.participant,
                    phase=s.phase,
                    **file_kwarg
                )
                new_submission.save(ignore_submission_limits=True)

                submission_dump[new_submission.pk] = {}

                evaluate_submission.apply_async((new_submission.pk, s.phase.is_scoring_only))

            open("test_submissions.json", "w+").write(json.dumps(submission_dump))
