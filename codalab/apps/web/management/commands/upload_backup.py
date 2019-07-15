from os import remove
from os.path import join

from django.core.management.base import BaseCommand

from apps.web.tasks import _make_url_sassy
from apps.web.utils import _put_blob


class Command(BaseCommand):
    help = "Takes a database dump file and puts it on remote storage"

    def add_arguments(self, parser):
        parser.add_argument('--file', '-f', type=str, help="The name of a db backup in /app/backups", required=True,
                            dest='dump_name')

    def handle(self, *args, **options):
        dump_name = options.get('dump_name', None)
        if not dump_name:
            raise Exception("the relative dump file path is required -- it is stored in /app/backups so you do not "
                            "need to specify full path")

        dump_path = join("/app/backups", dump_name)

        # Upload it
        print "Uploading backup '{}'".format(dump_path)
        upload_url = _make_url_sassy('backups/{}'.format(dump_name), permission='w')
        _put_blob(upload_url, dump_path)

        # Clean up
        print "Success! Removing local dump file '{}'".format(dump_path)
        remove(dump_path)
