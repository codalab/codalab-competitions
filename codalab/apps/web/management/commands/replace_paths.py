import json
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """
    Replaces path in all file locations, i.e. when moving from Azure to Minio
    """

    def handle(self, *args, **options):
        """
            from django.db.models import F
            class CF(F):
                ADD = '||'

            CompetitionSubmission.objects.update(s3_file='https://newcodalab.lri.fr/prod-private/' + CF('file'))
            CompetitionDefBundle.objects.update(s3_config_bundle='https://newcodalab.lri.fr/prod-private/' + CF('config_bundle'))

            CompetitionSubmission.objects.update(file_url_base="https://newcodalab.lri.fr/prod-private/")
            Competition.objects.update(image_url_base="https://newcodalab.lri.fr/prod-public/")
        """

        pass
        # site = Site.objects.all()[0]
        # print 'Old site domain: %s' % site.domain
        # print 'Old site name: %s' % site.name
        #
        # if len(args) < 1:
        #     print 'Usage: <domain (e.g., worksheets.codalab.org)> [<name (e.g., CodaLab Worksheets)>]'
        #     return
        # domain = args[0]
        # name = args[1] if len(args) > 1 else domain
        #
        # site.domain = domain
        # site.name = name
        # site.save()
