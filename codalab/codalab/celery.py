from __future__ import absolute_import
from django.conf import settings
from celery import Celery
import os


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codalab.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

# Have to do this to make django-configurations work...
from configurations import importer
importer.install()

app = Celery('codalab')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.config_from_object('django.conf:settings')
app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# app.autodiscover_tasks()
from django.apps import apps
# app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.worker_prefetch_multiplier = 1

app.conf.beat_schedule = {
    # 'add-every-30-seconds': {
    #     'task': 'tasks.add',
    #     'schedule': 30.0,
    #     'args': (16, 16)
    # },
    'phase_migrations': {
        'task': 'apps.web.tasks.do_phase_migrations',
        'schedule': 300,
    },
    'chahub_retries': {
        'task': 'apps.web.tasks.do_chahub_retries',
        'schedule': 600,
    },
    'check_all_parent_submissions': {
        'task': 'apps.web.tasks.check_all_parent_submissions',
        'schedule': 60,
    },
    'check_worker_status': {
        'task': 'apps.web.tasks.change_worker_status',
        'schedule': 60,
    }
}
app.conf.timezone = 'UTC'
