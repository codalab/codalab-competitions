import time
import requests
import json
import re
import io, zipfile
import tempfile, os.path, subprocess, StringIO
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

def local_run(url, submission):
    """
        This routine will take the job (initially a competition submission, later a run) and execute it locally.
    """
    program = submission.phase.scoring_program.name
    dataset = submission.phase.reference_data.name
    base_dir = models.submission_root(submission)
    print "Running locally in directory: %s" % base_dir

    # Make a directory for the run
    job_dir = os.path.join(tempfile.gettempdir(), base_dir)
    print "Job Dir: %s" % job_dir
    if not os.path.exists(job_dir):
        os.makedirs(job_dir)
    else:
        print "Job dir already exists, clearing it out."
        os.rmdir(job_dir)
        os.makedirs(job_dir)

    input_dir = os.path.join(job_dir, "input")
    output_dir = os.path.join(job_dir, "output")
    program_dir = os.path.join(job_dir, "program")

    # Make the run/output directory
    for d in [os.path.join(input_dir, "ref"), os.path.join(input_dir, "res"), program_dir, output_dir]:
        os.makedirs(d)

    # Grab the program bundle, unpack it in the run/program directory
    pzip = zipfile.ZipFile(io.BytesIO(submission.phase.scoring_program.read()))
    pzip.extractall(os.path.join(job_dir, "program"))
    metadata = open(os.path.join(program_dir, "metadata")).readlines()
    for line in metadata:
        print line
        key, value = line.split(":")
        if "command" in key.lower():
            for cmdterm in value.split(" "):
                if "$program" in cmdterm:
                    prefix, cmd = cmdterm.split("/")
                    print cmd
    command = os.path.join(program_dir, cmd)

    # Grab the reference bundle, unpack in the run/input directory
    rzip = zipfile.ZipFile(io.BytesIO(submission.phase.reference_data.read()))
    rzip.extractall(os.path.join(job_dir, "input", "ref"))

    # Grab the submission bundle, unpack it in the directory
    szip = zipfile.ZipFile(io.BytesIO(submission.file.read()))
    szip.extractall(os.path.join(job_dir, "input", "res"))

    submission.set_status(models.CompetitionSubmissionStatus.RUNNING)
    submission.save()

    # Execute the job
    stdout_fn = os.path.join(output_dir, "stdout.txt")
    stderr_fn = os.path.join(output_dir, "stderr.txt")
    score_fn  = os.path.join(output_dir, "scores.txt")
    stdout_file = open(stdout_fn, 'wb')
    stderr_file = open(stderr_fn, 'wb')
    subprocess.call([command, input_dir, output_dir], stdout=stdout_file, stderr=stderr_file)
    stdout_file.close()
    stderr_file.close()

    # Pack up the output and store it in Azure.
    bytes = StringIO.StringIO()
    ozip = zipfile.ZipFile(bytes, 'w')
    ozip.write(score_fn, "scores.txt")
    ozip.close()
    bytes.seek(0)

    submission.output_file.save("output.zip", File(bytes))
    submission.stdout_file.save("stdout.txt", File(open(stdout_fn, 'r')))
    submission.stderr_file.save("stderr.txt", File(open(stderr_fn, 'r')))

def submission_get_status(submission_id):
    """
    Check on the status of a submission to the execution engine. If the submission was run locally, short circuit because it's finished.
    """
    # Handle the local execution case,  short-circuit and return Finished.
    if 'local' in settings.COMPUTATION_SUBMISSION_URL:
        print "%s: Local Execution, returning finished." % __name__
        return json.loads("{ \"Status\": \"Finished\" }")

    # Get the submission object
    print "%s: Retrieving submission object for id: %s" % (__name__, submission_id)
    submission = models.CompetitionSubmission.objects.get(pk=submission_id)

    # If the submission object has an execution key, retrieve the status and return the json
    if submission.execution_key:
        print "%s: Submission has an execution key, retrieving status from execution engine." % __name__
        res = requests.get(settings.COMPUTATION_SUBMISSION_URL + submission.execution_key)
        if res.status_code in (200,):
            print "%s: Submission status retrieved successfully." % __name__
            print "Status: %s" % res.json()
            return res.json()
        else:
            print "%s: Submission status not retreived succesfully." % __name__
            print "Status: %s\n%s" % (res.status_code, res.json())

    # Otherwise return None
    return None

@celery.task(name='competition.submission_run')
def submission_run(url, submission_id):
    time.sleep(0.01) # Needed temporarily for using sqlite. Race.
    submission = models.CompetitionSubmission.objects.get(pk=submission_id)

    if 'local' in settings.COMPUTATION_SUBMISSION_URL:
        print "Running locally."
        submission.set_status(models.CompetitionSubmissionStatus.SUBMITTED)
        submission.save()
        local_run(url, submission)
        submission.set_status(models.CompetitionSubmissionStatus.FINISHED, force_save=True)
        submission.save()
    else:
        print "Running against remote execution engine."
        program = submission.phase.scoring_program.name
        dataset = submission.phase.reference_data.name

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
        submission.stdout_file.save('stdout.txt', stdoutfile)
        submission.save()
        print "Generated files for input and run"

        # Submit the request to the computation service
        headers = {'content-type': 'application/json'}
        data = json.dumps({ "RunId" : submission.runfile.name, "Container" : settings.BUNDLE_AZURE_CONTAINER })
        print "Posting request to remote execution engine."
        res = requests.post(settings.COMPUTATION_SUBMISSION_URL, data=data, headers=headers)
        print "submitting: %s" % submission.runfile.name
        print "status: %d" % res.status_code
        print "%s" % res.json()
        if res.status_code in (200,201):
            data = res.json()
            submission.execution_key = data['Id']
            print "Setting status to submitted."
            submission.set_status(models.CompetitionSubmissionStatus.SUBMITTED)
        else:
            print "Setting status to failed."
            submission.set_status(models.CompetitionSubmissionStatus.FAILED)
        print "Saving submission."
        submission.save()
    print "Kicking of results retrieval task."
    submission_get_results.delay(submission.pk,1)
    return submission.pk


@celery.task(name='competition.submission_get_results')
def submission_get_results(submission_id,ct):
    print "%s: started" % __name__
    # TODO: Refactor
    # Hard-coded limits for now
    submission = models.CompetitionSubmission.objects.get(pk=submission_id)
    print "Got submission %d." % submission_id
    # Get status of computation from the computation engine
    status = submission_get_status(submission_id)
    print "Computation status: %s" % str(status)
    if status:
        if status['Status'] in ("Submitted"):
            submission.set_status(models.CompetitionSubmissionStatus.SUBMITTED, force_save=True)
            raise submission_get_results.retry(exc=Exception("An unexpected error has occurred."))
        if status['Status'] in ("Running"):
            submission.set_status(models.CompetitionSubmissionStatus.RUNNING, force_save=True)
            raise submission_get_results.retry(exc=Exception("An unexpected error has occurred."))        
        elif status['Status'] == "Finished":
            submission.set_status(models.CompetitionSubmissionStatus.FINISHED, force_save=True)
            return (submission.pk, ct, 'complete', status)
        elif status['Status'] == "Failed":
            submission.set_status(models.CompetitionSubmissionStatus.FAILED, force_save=True)
            return (submission.pk, ct, 'failed', status)
    else:
        return (submission.pk,ct,'failure',None)

@task_success.connect(sender=submission_get_results)
def submission_results_success_handler(sender,result=None,**kwargs):
    submission_id,ct,state,status = result
    submission = models.CompetitionSubmission.objects.get(pk=submission_id)
    if state == 'complete':
        print "Run is complete (submission.id: %s)" % submission.id
        submission.output_file.name = models.submission_file_blobkey(submission)
        submission.stderr_file.name = models.submission_stderr_filename(submission)
        submission.save()
        print "Retrieving output.zip and 'scores.txt' file"
        ozip = zipfile.ZipFile(io.BytesIO(submission.output_file.read()))
        scores = open(ozip.extract('scores.txt'), 'r').read()
        print "Processing scores..."
        for line in scores.split("\n"):
            if len(line) > 0:
                label, value = line.split(":")
                print "Processing |%s| => %s" % (label, value)
                try:
                    scoredef = models.SubmissionScoreDef.objects.get(competition=submission.phase.competition,  key=label.strip())
                    models.SubmissionScore.objects.create(result=submission, scoredef=scoredef, value=float(value))                    
                except models.SubmissionScoreDef.DoesNotExist as e:
                    print "Score '%s' does not exist" % label
                    pass
        print "Done processing scores..."
    else:
        raise Exception("An unexpected error has occurred.")

@task_success.connect(sender=submission_run)
def submission_run_success_handler(sender, result=None, **kwargs):
    print "Successful submission"

@task_failure.connect(sender=submission_run)
def submission_run_error_handler(sender, exception=None, **kwargs):
    submission_id = kwargs['kwargs']['submission_id']
    print "Handling failure for submission %s" % submission_id
    try:
        submission = models.CompetitionSubmission.objects.get(pk=submission_id)
        submission.set_status(models.CompetitionSubmissionStatus.FAILED, force_save=True)
    except:
        print "Unable to set Failed state of submission %s" % submission_id

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

@celery.task()
def echo(msg):
    print "Echoing %s" % (msg)

@celery.task()
def create_competition_from_bundle(comp_def_id):
    """
    create_competition_from_bundle(competition_definition_bundle_id):

    This method takes the id of an uploaded competition definition bundle (defined: https://github.com/codalab/codalab/wiki/12.-Building-a-Competition-Bundle)
    The result is a competition created in CodaLab that's ready to use.
    """
    print "Creating competition for new competition bundle."
    # Pull the competition from the database using the id passed in
    competition_def = models.CompetitionDefBundle.objects.get(pk=comp_def_id)
    return competition_def.unpack()

