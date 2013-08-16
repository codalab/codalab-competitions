from __future__ import absolute_import
from celery import Celery

celery = Celery('tasks' )
try:
    celery.config_from_envvar('CELERY_CONFIG')
except AttributeError:
    celery.conf.update( BROKER_URL='memory',
                        CELERY_IMPORTS = ('apps.web.tasks',)
                        )
if __name__ == '__main__':
    celery.start()
