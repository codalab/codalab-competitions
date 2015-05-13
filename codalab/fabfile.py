import warnings
import os
import sys

from fabric.api import cd, local, env, run, sudo, shell_env, quiet, hide, settings

env.setdefault("DJANGO_CONFIGURATION", "Dev")
from django.conf import settings as django_settings
from codalab.settings import Dev
django_settings.configure(Dev)


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Ignore annoying internal fabric depreciation stuff
warnings.filterwarnings("ignore", category=DeprecationWarning)


def fresh_db():
    print django_settings.DATABASES


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
        sys.stdout.write("Starting tmux...")
        local('./tmux.sh')
        print "done"
        return True


def stop_workers():
    local('tmux kill-session -t codalab_workers')


def test_e2e():
    sys.stdout.write("Running Selenium tests...")
    # insert selenium tests when we get them
    print "done"


def test_django():
    sys.stdout.write("Stopping workers...")
    local('python manage.py test', capture=True)
    print "done"


def test_lint():
    sys.stdout.write("Checking syntax...")
    local('flake8 **/*.py', capture=True)
    print "done"


def test():
    print "%" * 80
    print " Running tests..."
    print "%" * 80
    print ""

    with hide('running', 'stdout', 'stderr', 'warnings', 'aborts'):
        test_lint()
        test_django()
        test_e2e()
