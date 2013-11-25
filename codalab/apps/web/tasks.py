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
                              JobTaskResult,
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
        return JobTaskResult(status=Job.FINISHED)

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
        logger.info("Creating competition for competition bundle (bundle_id=%s, job_id=%s)",
                    comp_def_id, job.id)
        competition_def = CompetitionDefBundle.objects.get(pk=comp_def_id)
        competition = competition_def.unpack()
        logger.info("Created competition for competition bundle (bundle_id=%s, job_id=%s, comp_id=%s)",
                    comp_def_id, job.id, competition.pk)
        return JobTaskResult(status=Job.FINISHED, info={ 'competition_id': competition.pk })

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

        submission: The CompetitionSubmission object.
        """
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

    def submit_it():
        """Start the process to evaluate the given competition submission."""
        logger.debug("Entering evaluate_submission_task (job_id=%s)", job_id)
        submission_id = args['submission_id']
        submission = CompetitionSubmission.objects.get(pk=submission_id)
        logger.info("Dispatching evaluation request for competition submission (submission_id=%s, job_id=%s)",
                    submission_id, job_id)
        submit(submission)
        logger.info("Done dispatching evaluation request for competition submission (submission_id=%s, job_id=%s)",
                    submission_id, job_id)
        logger.debug("Leaving evaluate_submission_task (job_id=%s)", job_id)

    submit_it()

def evaluate_submission(submission_id):
    """
    Starts the process of evaluating a user's submission to a competition.

    submission_id: The ID of the CompetitionSubmission object.

    Returns a Job object which can be used to track the progress of the operation.
    """
    return Job.objects.create_and_dispatch_job('evaluate_submission', { 'submission_id': submission_id })

class SubmissionUpdateException(Exception):
    """Defines an exception that occurs during the update of a CompetitionSubmission object."""
    def __init__(self, submission, inner_exception):
        super(SubmissionUpdateException, self).__init__(inner_exception.message)
        self.submission = submission
        self.inner_exception = inner_exception

def update_submission_task(job_id, args):
    """
    A task to update the status of an evaluating a submission in a competition.

    job_id: The ID of the job.
    args: A dictionary with the arguments for the task. Expected items are:
        args['status']: The evaluation status, which is one of 'running', 'finished' or 'failed'.
    """

    def update_submission(submission, status):
        """
        Updates the status of a submission.

        submission: The CompetitionSubmission object to update.
        status: The new status string: 'running', 'finished' or 'failed'.
        """
        if (status == 'running'):
            submission.set_status(CompetitionSubmissionStatus.RUNNING)
            submission.save()
            return Job.RUNNING

        if (status == 'finished'):
            submission.output_file.name = submission_file_blobkey(submission)
            submission.stderr_file.name = submission_stderr_filename(submission)
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

    def handle_update_exception(job, ex):
        """
        Handles exception that occur while attempting to update the status of a submission.

        job: The running Job instance.
        ex: The exception. The handler tries to acquire the CompetitionSubmission instance
            from a submission attribute on the exception.
        """
        try:
            submission = ex.submission
            submission.set_status(CompetitionSubmissionStatus.FAILED)
            submission.save()
        except Exception:
            logger.exception("Unable to set the submission status to Failed (job_id=%s)", job.id)
        return JobTaskResult(status=Job.FAILED)

    def update_it(job):
        """Updates the database to reflect the state of the evaluation of the given competition submission."""
        logger.debug("Entering update_submission_task::update_it (job_id=%s)", job.id)
        if (job.task_type != 'evaluate_submission'):
            raise ValueError("Job has incorrect task_type (job.task_type=%s)", job.task_type)
        task_args = job.get_task_args()
        submission_id = task_args['submission_id']
        logger.debug("Looking for submission (job_id=%s, submission_id=%s)", job.id, submission_id)
        submission = CompetitionSubmission.objects.get(pk=submission_id)
        status = args['status']
        logger.debug("Ready to update submission status (job_id=%s, submission_id=%s, status=%s)",
                     job.id, submission_id, status)
        result = None
        try:
            result = update_submission(submission, status)
        except Exception as e:
            logger.exception("Failed to update submission (job_id=%s, submission_id=%s, status=%s)",
                             job.id, submission_id, status)
            raise SubmissionUpdateException(submission, e)
        return JobTaskResult(status=result)

    run_job_task(job_id, update_it, handle_update_exception)
