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
    time.sleep(4) # Needed temporarily for using sqlite. Race.
    program = 'competition/1/1/data/program.zip'
    dataset = 'competition/1/1/data/reference.zip'

    submission = models.CompetitionSubmission.objects.get(pk=submission_id)
    inputfile = ContentFile(
"""ref: %s
res: %s
""" % (dataset, submission.file.name))   
    submission.inputfile.save('input.txt', inputfile)
    runfile = ContentFile(
"""program: %s
input: %s
""" % (program, submission.inputfile.name))
    submission.runfile.save('run.txt', runfile)
    submission.save()
    headers = {'content-type': 'application/json'}
    data = json.dumps(submission.runfile.name)
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
        print "Run is complete"
        # Get files
        blobservice = BlobService(account_name=settings.AZURE_ACCOUNT_NAME, account_key=settings.AZURE_ACCOUNT_KEY)
        output_keyname = models.submission_file_blobkey(submission, "run/output.zip")
        stdout_keyname = models.submission_file_blobkey(submission, "run/stdout.txt")
        # stderr_keyname = models.submission_file_blobkey(submission, "stderr.txt")
        print "Retrieving blobs..."
        stdout = blobservice.get_blob(settings.BUNDLE_AZURE_CONTAINER, stdout_keyname)
        # stderr = blobservice.get_blob(settings.BUNDLE_AZURE_CONTAINER, stderr_keyname)

        # Open the zip file and extract scores.txt
        ozip = zipfile.ZipFile(io.BytesIO(blobservice.get_blob(settings.BUNDLE_AZURE_CONTAINER, output_keyname)))
        print "Retrieved all blobs and opened output.zip."
        scores = open(ozip.extract('scores.txt'), 'r').read()
        print "Processing scores..."
        for line in scores.split("\n"):
            if len(line) > 0:
                result = models.SubmissionResult.objects.create(submission=submission, aggregate=0.0)
                labels = ["Filename", "Dice", "Jaccard", "Sensitivity", "Precision", "Average Distance", "Hausdorff Distance", "Kappa", "Labels"]
                for label,value in zip(labels, line.split(",")):
                    print "Label: %s" % label
                    print "Value: %s" % value
                    if label == "Filename":
                        result.name = value.lstrip("..\\input\\res\\")
                        result.save()
                    elif label == "Labels":
                        result.notes = value
                        result.save()
                    elif label not in ["Filename", "Labels"]:
                        if label == "Dice":
                            result.aggregate = float(value)
                            result.save()
                        models.SubmissionScore.objects.create(result=result, label=label, value=float(value))
                    else:
                        print "Error parsing scores.txt"
    elif state == 'limit_exceeded':
        print "Run limit, or time limit exceeded."
    elif state == 'failure':
        print "Some failure happened"

@task_success.connect(sender=submission_run)
def submission_run_success_handler(sender, result=None, **kwargs):
    print "Successful submission"
    # Fill in Dummy data
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
