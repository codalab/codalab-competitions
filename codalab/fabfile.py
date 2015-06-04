import warnings
import os
import sys

from fabric.api import env
from fabric.api import hide
from fabric.api import local
from fabric.api import quiet
from fabric.colors import red, green

from django.core.exceptions import ImproperlyConfigured

env.setdefault("DJANGO_CONFIGURATION", "Dev")
from django.conf import settings as django_settings
try:
    from codalab.settings import Dev
    django_settings.configure(Dev)
except ImproperlyConfigured, e:
    print 'ERROR: Configuration issue:'
    print '\t', e
    print ''


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Ignore annoying internal fabric depreciated stuff
warnings.filterwarnings("ignore", category=DeprecationWarning)


def _print(str):
    sys.stdout.write(str)
    sys.stdout.flush()


###############################################################################
# Site/compute workers
###############################################################################
def view_workers():
    with quiet():
        if not local('tmux attach -t codalab_workers').succeeded:
            print 'No workers started, please use fab start_workers first'


def start_workers():
    '''starts compute + site workers in the background, use view_workers to look at the output'''
    with quiet():
        if not local('tmux -V').succeeded:
            print 'Please install tmux before running this command, i.e. "brew install tmux"'
            return
        _print("Starting tmux...")

        if local('tmux has-session -t codalab_workers').succeeded:
            print green("session already started! fab view_workers to view it.")
            return

        if local('./tmux.sh').succeeded:
            print green("done")
        else:
            print red("could not start workers!")


def stop_workers():
    with quiet():
        _print("Stopping tmux...")
        local('tmux kill-session -t codalab_workers')
        print green("done")


def restart_workers():
    stop_workers()
    start_workers()


###############################################################################
# Tests
###############################################################################
def test_e2e():
    with hide('running', 'stdout', 'stderr', 'warnings', 'aborts'):
        _print("Running Selenium tests...")
        # insert selenium tests when we get them
        print green("done")


def test_django():
    with hide('running', 'stdout', 'stderr', 'warnings', 'aborts'):
        _print("Running Django tests...")
        local('python manage.py test --noinput', capture=True)
        print green("done")


# def test_lint():
#     with hide('running', 'stdout', 'stderr', 'warnings', 'aborts'):
#         _print("Checking syntax...")
#         local(
#             'flake8 . --max-line-length=120 --exclude=*/migrations/* --ignore=E712,E127,F403,E128,E126,E711,E501',
#             capture=True
#         )
#         print "done"


def test():
    print "%" * 80
    print " Running all tests..."
    print "%" * 80
    print ""

    #test_lint()
    test_django()
    test_e2e()


###############################################################################
# Environment/database
###############################################################################
def fresh_db():
    raise NotImplementedError()


# for custom local helper fabric file, useful if doing something with keys
try:
    from local_fabfile import *
except Exception, e:
    pass
