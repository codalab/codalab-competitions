from __future__ import absolute_import

from celery import Celery
from celery import task

celery = Celery('tasks', backend='amqp', )
celery.config_from_object('celeryconfig')

# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)


# Tasks for competitions
# Currently stubs to test functionality
@task
def validate_submission(url):
    """
    Will validate the format of a submission.
    """
    return url

@task
def evaluate_submission(url):
    # evaluate(inputdir, standard, outputdir)
    return url


# For starting the process
if __name__ == '__main__':
    celery.start()
