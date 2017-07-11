from django.core.management.base import BaseCommand

from apps.web.models import Competition, CompetitionSubmission, CompetitionSubmissionStatus


class Command(BaseCommand):

    def handle(self, *args, **options):
        submissions = CompetitionSubmission.objects.filter(
            status__codename=CompetitionSubmissionStatus.FINISHED
        ).distinct('phase__competition')
        print(submissions)
