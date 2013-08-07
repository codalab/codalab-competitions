from configurations import importer
importer.install()

from django.conf import settings
from django.dispatch import receiver
from compsrv.celerysrv import celery
from celery.signals import task_success, task_failure, task_revoked, task_sent

import models

@celery.task(name='competition.validate_submission')
def validate_submission(url,submission_id):
    """
    Will validate the format of a submission.
    """
    print "VALIDATION %s" % url
    return submission_id

@celery.task(name='competition.evaluation_submission')
def evaluate_submission(url,submission_id):
    # evaluate(inputdir, standard, outputdir)
    return submission_id

@task_success.connect
def task_success_handler(sender, result=None, **kwargs):
    s = models.CompetitionSubmission.objects.get(pk=result)
    s.set_status('rejected', force_save=True)
   
