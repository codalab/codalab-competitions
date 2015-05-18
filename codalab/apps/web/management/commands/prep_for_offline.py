import datetime
import os
import requests
import shutil
import tempfile
import sys
import zipfile
import os


from optparse import make_option

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

class Command(BaseCommand):
    help = """Sets up Codalab for offline useage."""

    option_list = BaseCommand.option_list + (
        make_option('--delete', '-d',
                    dest='delete',
                    action="store_true",
                    default=False,
                    help="remove prep for offline"
                    ),
    )

    def handle(self, *args, **options):
        print " ----- "
        if options['delete']:
            print "cleaning up MathaJax"
            shutil.rmtree("apps/web/static/js/vendor/mathjax")
            return
        mathjax_url = 'https://github.com/mathjax/MathJax/archive/master.zip'
        #mathjax_url = 'https://github.com/mathjax/MathJax/archive/2.5.1.zip'
        file_name = 'mathjax.zip'
        dir_name = 'MathJax-master'
        if not os.path.exists(file_name):
            with open(file_name, "wb") as f:
                    print "Downloading %s to %s..." % (mathjax_url, file_name)
                    response = requests.get(mathjax_url, stream=True)
                    total_length = response.headers.get('content-length')
                    if total_length is None: # no content length header
                        f.write(response.content)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        for data in response.iter_content(1024*1024):
                            dl += len(data)
                            f.write(data)
                            done = int(50 * dl / total_length)
                            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                            sys.stdout.flush()

        if not os.path.exists(dir_name):
            print 'Unzipping %s to %s...' % (file_name, dir_name)
            zip_file = zipfile.ZipFile(file_name)
            zip_file.extractall()

        print "Moving over files to correct directories..."
        try:
            shutil.move(dir_name, 'apps/web/static/js/vendor/mathjax')
            #shutil.copytree(dir_name + "/fonts", "apps/web/static/js/vendor/mathjax")
            #shutil.copytree(dir_name + "/config", "apps/web/static/js/vendor/mathjax")
            #shutil.copytree(dir_name + "/extensions", "apps/web/static/js/vendor/mathjax")
            #shutil.copytree(dir_name + "/jax", "apps/web/static/js/vendor/mathjax")
            #shutil.copytree(dir_name + "/localization", "apps/web/static/js/vendor/mathjax")
            #shutil.copytree(dir_name + "/MathJax.js", "apps/web/static/js/vendor/mathjax/MathJax.js")
        except Exception, e:
            print "************"
            print "ERROR: MathJax files not found. Please rerun to download and unpack the files again"
            print e
            print "************"
            return

        #shutil.rmtree(dir_name)
        #os.remove(file_name)

        print "\n"
        print "Please put"
        print "LOCAL_MATHJAX = True"
        print "in your local.py settings file to load files for offline usage"
        print "\n"
