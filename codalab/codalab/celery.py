from __future__ import absolute_import

import os
import django

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codalab.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

django.setup()

from django.conf import settings  # noqa

# Have to do this to make django-configurations work...
from configurations import importer
importer.install()

app = Celery('codalab')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.config_from_object('django.conf:settings', namespace='CELERY')
