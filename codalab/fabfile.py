import os

from fabric.api import cd, local, env, run, sudo, shell_env, quiet, settings

env.setdefault("DJANGO_CONFIGURATION", "Dev")
from django.conf import settings as django_settings
from codalab.settings import Dev
django_settings.configure(Dev)


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def fresh_db():
    print django_settings.DATABASES


def view_workers():
    local('tmux attach -t codalab_workers')


# def start_workers():
#     '''This command stops any existing workers and starts the site/compute workers'''
#     with settings(warn_only=True):
#         local('tmux kill-session -t codalab_workers')
#
#
#
#     #try to do tmux
#     # if it fails, brew install tmux
#     with quiet():
#         if not local('tmux').succeeded:
#             print 'Please install tmux before running this command, i.e. "brew install tmux"'
#             return
#
#     compute_worker_dir = os.path.join(CURRENT_DIRECTORY, 'codalabtools', 'compute')
#     site_worker_dir = os.path.join(CURRENT_DIRECTORY, 'codalab')
#
#     # local('screen -d -S codalab_compute_worker -m "cd %s && python worker.py"' % compute_worker_dir)
#     #
#
#     # local('screen -d -S codalab_site_worker -m "cd %s && python worker.py"' % site_worker_dir)
#
#     local('./tmux.sh')
#     #local('nohup tmux new -d -s codalab_workers; sleep 1')
#     #local('nohup ./tmux.sh >& /dev/null < /dev/null &')
#     #local('tmux detach -t codalab_workers')
#     #local('tmux send -t codalab_workers.0 "workon codalab && cd %s && python worker" ENTER' % compute_worker_dir)
#     # local('tmux send-keys "workon codalab && cd %s && python worker"' % compute_worker_dir)
#     # local('tmux split-window')
#     ####### tmux selectp -t 0
#     # tmux


def test_e2e():
    pass


def test_django():
    local('python manage.py test')


def test_lint():
    local('flake8 **/*.py')


def test():
    test_lint()
    test_django()
    test_e2e()
