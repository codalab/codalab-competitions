import os
import sys
import warnings
import yaml

from fabric.api import env, hide, local, quiet, run, warn_only
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


###############################################################################
# Helpers
def _print(str):
    sys.stdout.write(str)
    sys.stdout.flush()


###############################################################################
# DevOps
def hosts(key):
    """Loads hosts from server_config.yaml in the format of:
            host_key:
              hosts:
                - hostname1
                - hostname2
        """
    assert os.path.exists('server_config.yaml'), "server_config.yaml does not exist next to fabfile.py"
    hosts = yaml.load(open('server_config.yaml').read())
    env.hosts = hosts[key]['hosts']


def compute_worker_update():
    """Updates compute workers to latest docker image

    Meant to be used with `hosts` like so:
        fab hosts:prod_workers compute_worker_update
    """
    with warn_only():
        # Error if compute_worker isn't already running
        run('docker kill compute_worker')
        run('docker rm compute_worker')
    run('docker pull ckcollab/competitions-v1-compute-worker:latest')
    run("docker run "
            "--env-file .env "
            "-v /var/run/docker.sock:/var/run/docker.sock "
            "-v /tmp/codalab:/tmp/codalab "
            "-d --restart unless-stopped "
            "--name compute_worker -- "
            "ckcollab/competitions-v1-compute-worker:latest")


def compute_worker_status():
    """Prints out `docker ps` for each worker

    Meant to be used with `hosts` like so:
        fab hosts:prod_workers compute_worker_status
    """
    run('docker ps')


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
