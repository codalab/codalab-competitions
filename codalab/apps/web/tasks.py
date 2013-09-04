import time
import requests
import json
import re
import zipfile
import io
from django.conf import settings
from django.dispatch import receiver
from django.core.files import File
from django.core.files.base import ContentFile

import celery
from celery.signals import task_success, task_failure, task_revoked, task_sent
from codalab.settings import base

from azure.storage import *

import models

main = base.Base.SITE_ROOT

@celery.task(name='competition.submission_run')
def submission_run(url,submission_id):
    time.sleep(0.1) # Needed temporarily for using sqlite. Race.
    program = 'competition/1/1/data/program.zip'
    dataset = 'competition/1/1/data/reference.zip'

    submission = models.CompetitionSubmission.objects.get(pk=submission_id)
    # Generate input bundle pointing to reference/truth/gold dataset (ref) and user predictions (res).
    inputfile = ContentFile(
"""ref: %s
res: %s
""" % (dataset, submission.file.name))   
    submission.inputfile.save('input.txt', inputfile)
    # Generate run bundle, which binds the input bundle to the scoring program
    runfile = ContentFile(
"""program: %s
input: %s
""" % (program, submission.inputfile.name))
    submission.runfile.save('run.txt', runfile)
    # Log start of evaluation to stdout.txt
    stdoutfile = ContentFile(
"""Standard output file for submission #%s:

""" % (submission.submission_number))
    submission.stdout_file.save('run/stdout.txt', stdoutfile)
    submission.save()
    # Submit the request to the computation service
    headers = {'content-type': 'application/json'}
    data = json.dumps({ "RunId" : submission.runfile.name, "Container" : settings.BUNDLE_AZURE_CONTAINER })
    res = requests.post(settings.COMPUTATION_SUBMISSION_URL, data=data, headers=headers)
    print "submitting: %s" % submission.runfile.name
    if res.status_code in (200,201):
        data = res.json()
        submission.execution_key = data['Id']
        submission.set_status('processing')
    else:
        submission.set_status('processing_failed')
    submission.save()
    submission_get_results.delay(submission.pk,1)
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

@celery.task(name='competition.submission_get_results')
def submission_get_results(submission_id,ct):
    # TODO: Refactor
    # Hard-coded limits for now
    submission = models.CompetitionSubmission.objects.get(pk=submission_id)
    if ct > 1000:
        # return None to indicate bailing on checking
        return (submission.pk,ct,'limit_exceeded',None)
    status = submission.get_execution_status()
    print "Status: %s" % str(status)
    if status:
        submission.set_status(status['Status'].lower(), force_save=True)
        if status['Status'] in ("Submitted","Running"):
            return (submission.pk, ct+1, 'rerun', None)
        elif status['Status'] == "Finished":
            return (submission.pk, ct, 'complete', status)
        elif status['Status'] == "Failed":
            return (submission.pk, ct, 'failed', status)
    else:
        return (submission.pk,ct,'failure',None)
    
@task_success.connect(sender=submission_get_results)
def submission_results_success_handler(sender,result=None,**kwargs):
    submission_id,ct,state,status = result
    submission = models.CompetitionSubmission.objects.get(pk=submission_id)
    if state == 'rerun':
        print "Querying for results again"
        submission_get_results.apply_async((submission_id,ct),countdown=5)
    elif state == 'complete':
        print "Run is complete (submission.id: %s)" % submission.id
        submission.output_file.name = models.submission_file_blobkey(submission)
        submission.stderr_file.name = models.submission_stderr_filename(submission)
        submission.save()
        print "Retrieving output.zip and 'scores.txt' file"
        ozip = zipfile.ZipFile(io.BytesIO(submission.output_file.read()))
        scores = open(ozip.extract('scores.txt'), 'r').read()
        print "Processing scores..."
        first = True
        result = models.SubmissionResult.objects.create(submission=submission, aggregate=0.0)
        result.name = submission.submission_number
        result.save()
        for line in scores.split("\n"):
            if len(line) > 0:
                label, value = line.split(":")
                if first:
                    first = False
                    result.aggregate = float(value)
                    result.save()
                try:
                    scoredef = models.SubmissionScoreDef.objects.get(competition=submission.phase.competition,  key=label.strip())
                    models.SubmissionScore.objects.create(result=result, scoredef=scoredef, value=float(value))
                except SubmissionScoreDef.DoesNotExist as e:
                    print "Score %s does not exist" % label
                    pass
                    
        print "Done processing scores..."
    elif state == 'limit_exceeded':
        print "Run limit, or time limit exceeded."
    else:
        print "A failure happened"

@task_success.connect(sender=submission_run)
def submission_run_success_handler(sender, result=None, **kwargs):
    print "Successful submission"
    #Fill in Dummy data
    # import random
    # s = models.CompetitionSubmission.objects.get(pk=result)
    # s.set_status('accepted', force_save=True)
    # subres = models.SubmissionResult.objects.create(submission=s,aggregate=0)
    # scores = []
    # for s in ['score1','score2','score3']:
    #     rs = random.random()*10
    #     sc = models.SubmissionScore.objects.create(result=subres,label=s,value=rs)
    #     scores.append(rs)
    # subres.aggregate = sum(scores)/len(scores)
    # subres.save()
    # print " ACCEPTED SUBMISSION %s" % str(sender)

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
