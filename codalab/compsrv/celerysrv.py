from __future__ import absolute_import
from celery import Celery

celery = Celery('tasks' )
celery.config_from_envvar('CELERY_CONFIG')

if __name__ == '__main__':
    celery.start()
