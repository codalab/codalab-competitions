#from configurations import importer
#importer.install()

import time
from django.conf import settings
from django.dispatch import receiver
#from compsrv.celerysrv import celery
import celery
from celery.signals import task_success, task_failure, task_revoked, task_sent
from codalab.settings import base

import models

main = base.Base.SITE_ROOT

@celery.task(name='competition.submission_run')
def submission_run(url,submission_id):
    ## Only a simulation
    
    time.sleep(3) # This is here because of sqlite
    submission = models.CompetitionSubmission.objects.get(pk=submission_id)
    
    print "Submitting"
    return submission.pk

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

@task_success.connect(sender=submission_run)
def task_success_handler(sender, result=None, **kwargs):
    import random
    s = models.CompetitionSubmission.objects.get(pk=result)
    s.set_status('accepted', force_save=True)
    subres = models.SubmissionResult.objects.create(submission=s,aggregate=0)
    scores = []
    for s in ['score1','score2','score3']:
        rs = random.random()*10
        sc = models.SubmissionScore.objects.create(result=subres,label=s,value=rs)
        scores.append(rs)
    subres.aggregate = sum(scores)/len(scores)
    subres.save()
    print " ACCEPTED SUBMISSION %s" % str(sender)


# Bundle Tasks
@celery.task
def create_directory(bundleid):
    import subprocess
    bundle = models.Bundle.objects.get(id=bundleid)
    args = ['cd repositories && mkdir -p '+ bundle.name]
    subprocess.check_output(args, shell=True)
    bundle.path = main+'/repositories/'+bundle.name
    bundle.save()
    print bundle.path
    sub_directories.delay(bundleid)


@celery.task
def sub_directories(bundleid):
    import subprocess
    bundle = models.Bundle.objects.get(id=bundleid)
    args = ['cd repositories/'+bundle.name+' && mkdir -p input && mkdir -p output']
    subprocess.check_output(args, shell=True)
    bundle.inputpath = bundle.path+'/input'
    bundle.outputpath = bundle.path+'/output'
    bundle.save()
    print "The directories have been created"
    args = ['cd '+bundle.path+' && touch bundle.yaml']
    subprocess.check_output(args, shell=True)
    bundle.save()
    print "The bundle yaml has been created"
