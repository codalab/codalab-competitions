"""
Defines background tasks needed by the web site.
"""
import io
import json
import logging
from zipfile import ZipFile
from django.conf import settings
from django.core.files.base import ContentFile
from apps.jobs.models import (Job,
                              run_job_task,
                              getQueue)
from apps.web.models import (CompetitionSubmission,
                             CompetitionDefBundle,
                             CompetitionSubmissionStatus,
                             submission_file_blobkey,
                             submission_stderr_filename,
                             SubmissionScore,
                             SubmissionScoreDef)

logger = logging.getLogger(__name__)

# Echo

def echo_task(job_id, args):
    """
    A simple task to echo a message provided as args['message']. The associated job will
    be marked as Finished if the message is echoes successfully. Otherwise the job will be
    marked as Failed.

    job_id: The ID of the job.
    args: A dictionary with the arguments for the task. Expected items are:
        args['message']: string to send as info to the module's logger.
    """
    def echo_it(job):
        """Echoes the message specified."""
        logger.info("Echoing (job id=%s): %s", job.id, args['message'])
        return Job.FINISHED

    run_job_task(job_id, echo_it)

def echo(text):
    """
    Echoes the text specified. This is for testing.

    text: The text to echo.

    Returns a Job object which can be used to track the progress of the operation.
    """
    return Job.objects.create_and_dispatch_job('echo', { 'message': text })

# Create competition

def create_competition_task(job_id, args):
    """
    A task to create a competition from a bundle with the competition's definition.

    job_id: The ID of the job.
    args: A dictionary with the arguments for the task. Expected items are:
        args['comp_def_id']: The ID of the bundle holding the competition definition.
    Once the task succeeds, a new competition will be ready to use in CodaLab.
    """
    def create_it(job):
        """Handles the actual creation of the competition"""
        comp_def_id = args['comp_def_id']
        logger.info("Creating competition for competition bundle (bundle_id=%s, job_id=%s)", comp_def_id, job.id)
        competition_def = CompetitionDefBundle.objects.get(pk=comp_def_id)
        competition_def.unpack()
        logger.info("Created competition for competition bundle (bundle_id=%s, job_id=%s)", comp_def_id, job.id)
        return Job.FINISHED

    run_job_task(job_id, create_it)

def create_competition(comp_def_id):
    """
    Starts the process of creating a competition given a bundle with the competition's definition.

    comp_def_id: The ID of the bundle holding the competition definition.
                 See: https://github.com/codalab/codalab/wiki/12.-Building-a-Competition-Bundle.

    Returns a Job object which can be used to track the progress of the operation.
    """
    return Job.objects.create_and_dispatch_job('create_competition', { 'comp_def_id': comp_def_id })

# Evaluate submissions in a competition

def evaluate_submission_task(job_id, args):
    """
    A task to start the evaluation of a user's submission in a competition.

    job_id: The ID of the job.
    args: A dictionary with the arguments for the task. Expected items are:
        args['submission_id']: The ID of the CompetitionSubmission object.
    """

    def submit(submission):
        """
        Dispatches the evaluation of the given submission to an appropriate compute worker.

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
        # Submit the request to the computation service
        body = json.dumps({ "id" : job_id,
                            "task_type": "run",
                            "task_args": {
                                "bundle_id" : submission.runfile.name,
                                "container_name" : settings.BUNDLE_AZURE_CONTAINER,
                                "reply_to" : settings.SBS_RESPONSE_QUEUE
                            }
                          })
        getQueue(settings.SBS_COMPUTE_QUEUE).send_message(body)
        submission.execution_key = job_id
        submission.set_status(CompetitionSubmissionStatus.SUBMITTED)
        submission.save()
    print "Kicking of results retrieval task."
    submission_get_results.delay(submission.pk,1)
    return submission.pk

@celery.task(name='competition.submission_get_results', max_retries=50, default_retry_delay=15)
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
            logger.debug("Retrieving output.zip and 'scores.txt' file (submission_id=%s)", submission.id)
            ozip = ZipFile(io.BytesIO(submission.output_file.read()))
        scores = open(ozip.extract('scores.txt'), 'r').read()
            logger.debug("Processing scores... (submission_id=%s)", submission.id)
        for line in scores.split("\n"):
            if len(line) > 0:
                label, value = line.split(":")
    try:
                        scoredef = SubmissionScoreDef.objects.get(competition=submission.phase.competition,
                                                                         key=label.strip())
                        SubmissionScore.objects.create(result=submission, scoredef=scoredef, value=float(value))
                    except SubmissionScoreDef.DoesNotExist:
                        logger.warning("Score %s does not exist (submission_id=%s)", label, submission.id)
            logger.debug("Done processing scores... (submission_id=%s)", submission.id)
            submission.set_status(CompetitionSubmissionStatus.FINISHED)
            submission.save()
            return Job.FINISHED

        if (status != 'failed'):
            logger.error("Invalid status: %s (submission_id=%s)", status, submission.id)
        submission.set_status(CompetitionSubmissionStatus.FAILED)
        submission.save()

@celery.task()
def create_competition_from_bundle(competition_bundle):
    """
        Handles exception that occur while attempting to update the status of a submission.

        job: The running Job instance.
        ex: The exception. The handler tries to acquire the CompetitionSubmission instance
            from a submission attribute on the exception.
    """
    print "Creating competition for new competition bundle."
    return competition_bundle.unpack()

    run_job_task(job_id, update_it, handle_update_exception)
