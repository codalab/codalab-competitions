"""
Defines background tasks needed by the web site.
"""
import csv
import io
import json
import logging
import StringIO
import traceback
import yaml
import zipfile

from urllib import pathname2url

from django.core.exceptions import ObjectDoesNotExist
from yaml.representer import SafeRepresenter
from zipfile import ZipFile
from collections import OrderedDict

import sys

from datetime import datetime
from boto.s3.connection import S3Connection
from celery import task
from celery.app import app_or_default
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.files.base import ContentFile
from django.core.mail import get_connection, EmailMultiAlternatives, send_mail
from django.db import transaction
from django.db.models import Count
from django.template import Context
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from apps.chahub.models import ChaHubSaveMixin
from apps.jobs.models import (Job,
                              run_job_task,
                              JobTaskResult,
                              getQueue, update_job_status_task)
from apps.web.models import (add_submission_to_leaderboard,
                             Competition,
                             CompetitionSubmission,
                             CompetitionDefBundle,
                             CompetitionSubmissionStatus,
                             CompetitionPhase,
                             submission_prediction_output_filename,
                             submission_output_filename,
                             submission_detailed_results_filename,
                             submission_private_output_filename,
                             submission_stdout_filename,
                             submission_stderr_filename,
                             submission_history_file_name,
                             submission_scores_file_name,
                             submission_coopetition_file_name,
                             predict_submission_stdout_filename,
                             predict_submission_stderr_filename,
                             SubmissionScore,
                             SubmissionScoreDef,
                             CompetitionSubmissionMetadata, BundleStorage, SubmissionResultGroup,
                             SubmissionScoreDefGroup)
from apps.coopetitions.models import DownloadRecord

import time
# import cProfile
from apps.web.utils import inheritors
from codalab.azure_storage import make_blob_sas_url

from apps.web import models

from apps.web.models import CompetitionDump

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
    return Job.objects.create_and_dispatch_job('echo', {'message': text})


@task(queue='site-worker', soft_time_limit=60 * 60 * 24)
def create_competition(job_id, comp_def_id):
    """
    A task to create a competition from a bundle with the competition's definition.

    job_id: The ID of the job.
    args: A dictionary with the arguments for the task. Expected items are:
        args['comp_def_id']: The ID of the bundle holding the competition definition.
    Once the task succeeds, a new competition will be ready to use in CodaLab.
    """

    logger.info("Creating competition for competition bundle (bundle_id=%s)", comp_def_id)
    competition_def = CompetitionDefBundle.objects.get(pk=comp_def_id)
    try:
        competition = competition_def.unpack()
        result = JobTaskResult(status=Job.FINISHED, info={'competition_id': competition.pk})
        update_job_status_task(job_id, result.get_dict())
        logger.info("Created competition for competition bundle (bundle_id=%s, comp_id=%s)",
                    comp_def_id, competition.pk)

    except Exception as e:
        result = JobTaskResult(status=Job.FAILED, info={'error': str(e)})
        update_job_status_task(job_id, result.get_dict())


# CompetitionSubmission states which are final.
_FINAL_STATES = {
    CompetitionSubmissionStatus.FINISHED,
    CompetitionSubmissionStatus.FAILED,
    CompetitionSubmissionStatus.CANCELLED
}

def _set_submission_status(submission_id, status_codename):
    """
    Update the status of a submission.

    submission_id: PK of CompetitionSubmission object.
    status_codename: New status codename.
    """
    status = CompetitionSubmissionStatus.objects.get(codename=status_codename)
    with transaction.commit_on_success():
        submission = CompetitionSubmission.objects.select_for_update().get(pk=submission_id)
        old_status_codename = submission.status.codename
        if old_status_codename not in _FINAL_STATES:
            submission.status = status
            submission.save()
            logger.info("Changed submission status from %s to %s (id=%s).",
                        old_status_codename, status_codename, submission_id)
        else:
            logger.info("Skipping update of submission status: invalid transition %s -> %s  (id=%s).",
                        status_codename, old_status_codename, submission_id)


def predict(submission, job_id):
    """
    Dispatches the prediction taks for the given submission to an appropriate compute worker.

    submission: The CompetitionSubmission object.
    job_id: The job ID used to track the progress of the evaluation.
    """
    # Generate metadata-only bundle describing the computation
    lines = []
    if settings.USE_AWS:
        program_value = submission.s3_file
    else:
        program_value = submission.file.name

    if len(program_value) > 0:
        lines.append("program: %s" % _make_url_sassy(program_value))
    else:
        raise ValueError("Program is missing.")

    if submission.phase.ingestion_program:
        # Keep stdout/stder for ingestion
        submission.ingestion_program_stdout_file.save('ingestion_program_stdout_file.txt', ContentFile(''))
        submission.ingestion_program_stderr_file.save('ingestion_program_stderr_file.txt', ContentFile(''))

        # For the ingestion program we have to include the actual ingestion program...
        lines.append("ingestion_program: %s" % _make_url_sassy(submission.phase.ingestion_program.name))

        # ..as well as the reference data for this phase.
        ref_value = submission.phase.reference_data.name
        if len(ref_value) > 0:
            lines.append("hidden_ref: %s" % _make_url_sassy(ref_value))

    # Create stdout.txt & stderr.txt, set the file names
    username = submission.participant.user.username
    stdout_filler = ["Standard output for submission #{0} by {1}.".format(submission.submission_number, username), ""]
    submission.stdout_file.save('stdout.txt', ContentFile('\n'.join(stdout_filler)))
    submission.prediction_stdout_file.save('prediction_stdout_file.txt', ContentFile('\n'.join(stdout_filler)))
    stderr_filler = ["Standard error for submission #{0} by {1}.".format(submission.submission_number, username), ""]
    submission.stderr_file.save('stderr.txt', ContentFile('\n'.join(stderr_filler)))
    submission.prediction_stderr_file.save('prediction_stderr_file.txt', ContentFile('\n'.join(stderr_filler)))

    submission.prediction_output_file.save('output.zip', ContentFile(''))

    input_value = submission.phase.input_data.name

    logger.info("Running prediction")

    if len(input_value) > 0:
        lines.append("input: %s" % _make_url_sassy(input_value))
    lines.append("stdout: %s" % _make_url_sassy(submission.prediction_stdout_file.name, permission='w'))
    lines.append("stderr: %s" % _make_url_sassy(submission.prediction_stderr_file.name, permission='w'))
    submission.prediction_runfile.save('run.txt', ContentFile('\n'.join(lines)))

    # Store workflow state
    submission.execution_key = json.dumps({'predict': job_id})
    submission.save()

    # Submit the request to the computation service
    _prepare_compute_worker_run(job_id, submission, is_prediction=True)

    # Update the submission object
    _set_submission_status(submission.id, CompetitionSubmissionStatus.SUBMITTED)


def _prepare_compute_worker_run(job_id, submission, is_prediction):
    """Kicks off the compute_worker_run task passing job id, submission container details, and "is prediction
    or scoring" flag to compute worker"""
    if is_prediction:
        bundle_url = submission.prediction_runfile.name
        stdout = submission.prediction_stdout_file.name
        stderr = submission.prediction_stderr_file.name
        output = submission.prediction_output_file.name

    else:
        # Scoring, if we're not predicting
        bundle_url = submission.runfile.name
        stdout = submission.stdout_file.name
        stderr = submission.stderr_file.name
        output = submission.output_file.name

    if submission.docker_image and submission.docker_image != "":
        docker_image = submission.docker_image
    else:
        docker_image = submission.phase.competition.competition_docker_image or settings.DOCKER_DEFAULT_WORKER_IMAGE
        submission.docker_image = docker_image
        submission.save()

    logger.info("@@@ Docker image set to: {} @@@".format(docker_image))

    data = {
        "id": job_id,
        "task_type": "run",
        "task_args": {
            "submission_id": submission.pk,
            "docker_image": docker_image,
            "ingestion_program_docker_image": docker_image,
            "bundle_url": _make_url_sassy(bundle_url),
            "stdout_url": _make_url_sassy(stdout, permission='w'),
            "stderr_url": _make_url_sassy(stderr, permission='w'),
            "output_url": _make_url_sassy(output, permission='w'),
            "ingestion_program_output_url": _make_url_sassy(submission.ingestion_program_stdout_file.name, permission='w'),
            "ingestion_program_stderr_url": _make_url_sassy(submission.ingestion_program_stderr_file.name, permission='w'),
            "detailed_results_url": _make_url_sassy(submission.detailed_results_file.name, permission='w'),
            "private_output_url": _make_url_sassy(submission.private_output_file.name, permission='w'),
            "secret": submission.secret,
            "execution_time_limit": submission.phase.execution_time_limit,
            "predict": is_prediction,
        }
    }

    logger.info("Passing task args to compute worker: %s", data["task_args"])

    time_limit = submission.phase.execution_time_limit
    if time_limit <= 0:
        time_limit = 60 * 10  # 10 minutes timeout by default

    if submission.phase.competition.queue:
        submission.queue_name = submission.phase.competition.queue.name or ''
        submission.save()

        # Send to special queue?
        app = app_or_default()
        with app.connection() as new_connection:
            new_connection.virtual_host = submission.phase.competition.queue.vhost
            compute_worker_run(data, soft_time_limit=time_limit, connection=new_connection)
    else:
        compute_worker_run(data, soft_time_limit=time_limit, priority=2)


def compute_worker_run(data, priority=None, **kwargs):
    if priority:
        kwargs['queue_arguments'] = {'x-max-priority': priority}
    task_args = data['task_args'] if 'task_args' in data else None
    app = app_or_default()
    app.send_task('compute_worker_run', args=(data["id"], task_args), queue='compute-worker', **kwargs)


def _make_url_sassy(path, permission='r', duration=60 * 60 * 24):
    if settings.USE_AWS:
        if permission == 'r':
            # GET instead of r (read) for AWS
            method = 'GET'
        elif permission == 'w':
            # GET instead of w (write) for AWS
            method = 'PUT'
        else:
            # Default to get if we don't know
            method = 'GET'

        # Remove the beginning of the URL (before bucket name) so we just have the path to the file
        path = path.split(settings.AWS_STORAGE_PRIVATE_BUCKET_NAME)[-1]

        # Spaces replaced with +'s, so we have to replace those...
        path = path.replace('+', ' ')

        return BundleStorage.connection.generate_url(
            expires_in=duration,
            method=method,
            bucket=settings.AWS_STORAGE_PRIVATE_BUCKET_NAME,
            key=path,
            query_auth=True,
        )
    else:
        sassy_url = make_blob_sas_url(
            settings.BUNDLE_AZURE_ACCOUNT_NAME,
            settings.BUNDLE_AZURE_ACCOUNT_KEY,
            settings.BUNDLE_AZURE_CONTAINER,
            path,
            permission=permission,
            duration=duration
        )

        # Ugly way to check if we didn't get the path, should work...
        if '<Code>InvalidUri</Code>' not in sassy_url:
            return sassy_url
        else:
            return ''


def score(submission, job_id):
    """
    Dispatches the scoring task for the given submission to an appropriate compute worker.

    submission: The CompetitionSubmission object.
    job_id: The job ID used to track the progress of the evaluation.
    """
    # profile = cProfile.Profile()
    start = time.time()
    # profile.enable()
    # Loads the computation state.
    state = {}
    if len(submission.execution_key) > 0:
        state = json.loads(submission.execution_key)
    has_generated_predictions = 'predict' in state

    #generate metadata-only bundle describing the history of submissions and phases
    last_submissions = CompetitionSubmission.objects.filter(
        participant=submission.participant,
        status__codename=CompetitionSubmissionStatus.FINISHED
    ).order_by('-submitted_at')


    lines = []
    # lines.append("description: history of all previous successful runs output files")
    #
    # if last_submissions:
    #     for past_submission in last_submissions:
    #         if past_submission.pk != submission.pk:
    #             #pad folder numbers for sorting os side, 001, 002, 003,... 010, etc...
    #             past_submission_phasenumber = '%03d' % past_submission.phase.phasenumber
    #             past_submission_number = '%03d' % past_submission.submission_number
    #             lines.append('%s/%s/output/: %s' % (
    #                     past_submission_phasenumber,
    #                     past_submission_number,
    #                     submission_private_output_filename(past_submission),
    #                 )
    #             )


    submission.history_file.save('history.txt', ContentFile('\n'.join(lines)))

    score_csv = submission.phase.competition.get_results_csv(submission.phase.pk)
    submission.scores_file.save('scores.txt', ContentFile(score_csv))

    # Extra submission info
    coopetition_zip_buffer = StringIO.StringIO()
    coopetition_zip_file = zipfile.ZipFile(coopetition_zip_buffer, "w")

    phases_list = submission.phase.competition.phases.all()

    for phase in phases_list:
        coopetition_field_names = (
            "participant__user__username",
            "pk",
            "when_made_public",
            "when_unmade_public",
            "started_at",
            "completed_at",
            "download_count",
            "submission_number",
        )
        annotated_submissions = phase.submissions.filter(status__codename=CompetitionSubmissionStatus.FINISHED).values(
            *coopetition_field_names
        ).annotate(like_count=Count("likes"), dislike_count=Count("dislikes"))

        # Add this after fetching annotated count from db
        coopetition_field_names += ("like_count", "dislike_count")

        coopetition_csv = StringIO.StringIO()
        writer = csv.DictWriter(coopetition_csv, coopetition_field_names)
        writer.writeheader()
        for row in annotated_submissions:
            writer.writerow(row)

        coopetition_zip_file.writestr('coopetition_phase_%s.txt' % phase.phasenumber, coopetition_csv.getvalue().encode('utf-8'))

    # Scores metadata
    for phase in phases_list:
        coopetition_zip_file.writestr(
            'coopetition_scores_phase_%s.txt' % phase.phasenumber,
            phase.competition.get_results_csv(phase.pk, include_scores_not_on_leaderboard=True)
        )

    # Download metadata
    coopetition_downloads_csv = StringIO.StringIO()
    writer = csv.writer(coopetition_downloads_csv)
    writer.writerow((
        "submission_pk",
        "submission_owner",
        "downloaded_by",
        "time_of_download",
    ))
    for download in DownloadRecord.objects.filter(submission__phase__competition=submission.phase.competition):
        writer.writerow((
            download.submission.pk,
            download.submission.participant.user.username,
            download.user.username,
            str(download.timestamp),
        ))

    coopetition_zip_file.writestr('coopetition_downloads.txt', coopetition_downloads_csv.getvalue().encode('utf-8'))

    # Current user
    coopetition_zip_file.writestr('current_user.txt', submission.participant.user.username.encode('utf-8'))
    coopetition_zip_file.close()

    # Save them all
    submission.coopetition_file.save('coopetition.zip', ContentFile(coopetition_zip_buffer.getvalue()))

    # Generate metadata-only bundle describing the inputs. Reference data is an optional
    # dataset provided by the competition organizer. Results are provided by the participant
    # either indirectly (has_generated_predictions is True i.e. participant provides a program
    # which is run to generate results) ordirectly (participant uploads results directly).
    lines = []
    ref_value = submission.phase.reference_data.name
    if len(ref_value) > 0:
        lines.append("ref: %s" % _make_url_sassy(ref_value))
    if settings.USE_AWS:
        res_value = submission.prediction_output_file.name if has_generated_predictions else submission.s3_file
    else:
        res_value = submission.prediction_output_file.name if has_generated_predictions else submission.file.name
    if len(res_value) > 0:
        lines.append("res: %s" % _make_url_sassy(res_value))
    else:
        raise ValueError("Results are missing.")

    lines.append("history: %s" % _make_url_sassy(submission.history_file.name))
    lines.append("scores: %s" % _make_url_sassy(submission.scores_file.name))
    lines.append("coopetition: %s" % _make_url_sassy(submission.coopetition_file.name))
    lines.append("submitted-by: %s" % submission.participant.user.username)
    lines.append("submitted-at: %s" % submission.submitted_at.replace(microsecond=0).isoformat())
    lines.append("competition-submission: %s" % submission.submission_number)
    lines.append("competition-phase: %s" % submission.phase.phasenumber)
    is_automatic_submission = False
    if submission.phase.auto_migration:
        # If this phase has auto_migration and this submission is the first in the phase, it is an automatic submission!
        submissions_this_phase = CompetitionSubmission.objects.filter(
            phase=submission.phase,
            participant=submission.participant
        ).count()
        is_automatic_submission = submissions_this_phase == 1

    lines.append("automatic-submission: %s" % is_automatic_submission)
    submission.inputfile.save('input.txt', ContentFile('\n'.join(lines)))


    # Generate metadata-only bundle describing the computation.
    lines = []
    program_value = submission.phase.scoring_program.name
    if len(program_value) > 0:
        lines.append("program: %s" % _make_url_sassy(program_value))
    else:
        raise ValueError("Program is missing.")
    lines.append("input: %s" % _make_url_sassy(submission.inputfile.name))
    lines.append("stdout: %s" % _make_url_sassy(submission.stdout_file.name, permission='w'))
    lines.append("stderr: %s" % _make_url_sassy(submission.stderr_file.name, permission='w'))
    lines.append("private_output: %s" % _make_url_sassy(submission.private_output_file.name, permission='w'))
    lines.append("output: %s" % _make_url_sassy(submission.output_file.name, permission='w'))
    submission.runfile.save('run.txt', ContentFile('\n'.join(lines)))

    # Create stdout.txt & stderr.txt
    if has_generated_predictions == False:
        username = submission.participant.user.username
        lines = ["Standard output for submission #{0} by {1}.".format(submission.submission_number, username), ""]
        submission.stdout_file.save('stdout.txt', ContentFile('\n'.join(lines)))
        lines = ["Standard error for submission #{0} by {1}.".format(submission.submission_number, username), ""]
        submission.stderr_file.save('stderr.txt', ContentFile('\n'.join(lines)))
    # Update workflow state
    state['score'] = job_id
    submission.execution_key = json.dumps(state)

    # Pre-save files so we can overwrite their names later
    submission.output_file.save('output_file.zip', ContentFile(''))
    submission.private_output_file.save('private_output_file.zip', ContentFile(''))
    submission.detailed_results_file.save('detailed_results_file.html', ContentFile(''))
    submission.save()
    # Submit the request to the computation service
    _prepare_compute_worker_run(job_id, submission, is_prediction=False)

    if has_generated_predictions == False:
        _set_submission_status(submission.id, CompetitionSubmissionStatus.SUBMITTED)

    time_elapsed = time.time() - start
    logger.info("It took: %f seconds to run" % time_elapsed)


class SubmissionUpdateException(Exception):
    """Defines an exception that occurs during the update of a CompetitionSubmission object."""
    def __init__(self, submission, inner_exception):
        super(SubmissionUpdateException, self).__init__(inner_exception.message)
        self.submission = submission
        self.inner_exception = inner_exception


@task(queue='submission-updates')
def update_submission(job_id, args, secret):
    """
    A task to update the status of a submission in a competition.

    job_id: The ID of the job.
    args: A dictionary with the arguments for the task. Expected items are:
        args['status']: The evaluation status, which is one of 'running', 'finished' or 'failed'.
    """

    def _update_submission(submission, status, job_id, traceback=None, metadata=None):
        """
        Updates the status of a submission.

        submission: The CompetitionSubmission object to update.
        status: The new status string: 'running', 'finished' or 'failed'.
        job_id: The job ID used to track the progress of the evaluation.
        """

        state = {}
        if len(submission.execution_key) > 0:
            logger.debug("update_submission_task loading state: %s", submission.execution_key)
            state = json.loads(submission.execution_key)
            logger.debug("update_submission_task state = %s" % submission.execution_key)

        if metadata:
            is_predict = 'score' not in state
            sub_metadata, created = CompetitionSubmissionMetadata.objects.get_or_create(
                is_predict=is_predict,
                is_scoring=not is_predict,
                submission=submission,
            )
            sub_metadata.__dict__.update(metadata)
            sub_metadata.save()
            logger.debug("saving extra metadata, was a new object created? %s" % created)

        if status == 'running':
            _set_submission_status(submission.id, CompetitionSubmissionStatus.RUNNING)
            return Job.RUNNING

        if status == 'finished':
            result = Job.FAILED
            if 'score' in state:
                logger.debug("update_submission_task loading final scores (pk=%s)", submission.pk)
                logger.debug("Retrieving output.zip and 'scores.txt' file (submission_id=%s)", submission.id)
                logger.debug("Output.zip location=%s" % submission.output_file.file.name)
                ozip = ZipFile(io.BytesIO(submission.output_file.read()))
                scores = None
                try:
                    scores = open(ozip.extract('scores.txt'), 'r').read()
                except Exception:
                    logger.error("Scores.txt not found, unable to process submission: %s (submission_id=%s)", status, submission.id)
                    _set_submission_status(submission.id, CompetitionSubmissionStatus.FAILED)
                    return Job.FAILED

                logger.debug("Processing scores... (submission_id=%s)", submission.id)
                for line in scores.split("\n"):
                    if len(line) > 0:
                        label, value = line.split(":")
                        logger.debug("Attempting to submit score %s:%s" % (label, value))
                        try:
                            scoredef = SubmissionScoreDef.objects.get(competition=submission.phase.competition,
                                                                      key=label.strip())
                            SubmissionScore.objects.create(result=submission, scoredef=scoredef, value=float(value))
                        except SubmissionScoreDef.DoesNotExist:
                            logger.warning("Score %s does not exist (submission_id=%s)", label, submission.id)
                logger.debug("Done processing scores... (submission_id=%s)", submission.id)
                _set_submission_status(submission.id, CompetitionSubmissionStatus.FINISHED)

                # Automatically submit to the leaderboard?
                if submission.phase.is_blind and not submission.phase.force_best_submission_to_leaderboard:
                    logger.debug("Adding to leaderboard... (submission_id=%s)", submission.id)
                    add_submission_to_leaderboard(submission)
                    logger.debug("Leaderboard updated with latest submission (submission_id=%s)", submission.id)

                if submission.phase.competition.force_submission_to_leaderboard and not submission.phase.force_best_submission_to_leaderboard:
                    add_submission_to_leaderboard(submission)
                    logger.debug("Force submission added submission to leaderboard (submission_id=%s)", submission.id)

                if submission.phase.force_best_submission_to_leaderboard:
                    # In this phase get the submission score from the column with the lowest ordering
                    score_def = submission.get_default_score_def()
                    top_score = SubmissionScore.objects.filter(result__phase=submission.phase, scoredef=score_def)
                    score_value = submission.get_default_score()
                    if score_def.sorting == 'asc':
                        # The first value in ascending is the top score, 1 beats 3
                        top_score = top_score.order_by('value').first()
                        if score_value >= top_score.value:
                            add_submission_to_leaderboard(submission)
                            logger.debug("Force best submission added submission to leaderboard in ascending order "
                                         "(submission_id=%s, top_score=%s, score=%s)", submission.id, top_score, score_value)
                    elif score_def.sorting == 'desc':
                        # The last value in descending is the top score, 3 beats 1
                        top_score = top_score.order_by('value').last()
                        if score_value <= top_score.value:
                            add_submission_to_leaderboard(submission)
                            logger.debug("Force best submission added submission to leaderboard in descending order "
                                         "(submission_id=%s, top_score=%s, score=%s)", submission.id, top_score, score_value)

                result = Job.FINISHED

                if submission.participant.user.email_on_submission_finished_successfully:
                    email = submission.participant.user.email
                    site_url = "https://%s%s" % (Site.objects.get_current().domain, submission.phase.competition.get_absolute_url())
                    send_mail(
                        'Submission has finished successfully!',
                        'Your submission to the competition "%s" has finished successfully! View it here: %s' %
                        (submission.phase.competition.title, site_url),
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False
                    )
            else:
                logger.debug("update_submission_task entering scoring phase (pk=%s)", submission.pk)
                # url_name = pathname2url(submission_prediction_output_filename(submission))
                # submission.prediction_output_file.name = url_name
                # submission.prediction_stderr_file.name = pathname2url(predict_submission_stdout_filename(submission))
                # submission.prediction_stdout_file.name = pathname2url(predict_submission_stderr_filename(submission))
                # submission.save()
                try:
                    score(submission, job_id)
                    result = Job.RUNNING
                    logger.debug("update_submission_task scoring phase entered (pk=%s)", submission.pk)
                except Exception:
                    logger.exception("update_submission_task failed to enter scoring phase (pk=%s)", submission.pk)
            return result

        if status != 'failed':
            logger.error("Invalid status: %s (submission_id=%s)", status, submission.id)

        if traceback:
            submission.exception_details = traceback
            submission.save()

        _set_submission_status(submission.id, CompetitionSubmissionStatus.FAILED)

    def handle_update_exception(job, ex):
        """
        Handles exception that occur while attempting to update the status of a submission.

        job: The running Job instance.
        ex: The exception. The handler tries to acquire the CompetitionSubmission instance
            from a submission attribute on the exception.
        """
        try:
            submission = ex.submission
            _set_submission_status(submission.id, CompetitionSubmissionStatus.FAILED)
        except Exception:
            logger.exception("Unable to set the submission status to Failed (job_id=%s)", job.id)
        return JobTaskResult(status=Job.FAILED)

    def update_it(job):
        """Updates the database to reflect the state of the evaluation of the given competition submission."""
        logger.debug("Entering update_submission_task::update_it (job_id=%s)", job.id)
        if job.task_type != 'evaluate_submission':
            raise ValueError("Job has incorrect task_type (job.task_type=%s)", job.task_type)
        task_args = job.get_task_args()
        submission_id = task_args['submission_id']
        logger.debug("Looking for submission (job_id=%s, submission_id=%s)", job.id, submission_id)
        submission = CompetitionSubmission.objects.get(pk=submission_id)

        if secret != submission.secret:
            raise SubmissionUpdateException(submission, "Password does not match")

        status = args['status']
        logger.debug("Ready to update submission status (job_id=%s, submission_id=%s, status=%s)",
                     job.id, submission_id, status)
        result = None
        try:
            traceback = None
            metadata = None
            if 'extra' in args:
                if 'traceback' in args['extra']:
                    traceback = args['extra']['traceback']

                if 'metadata' in args['extra']:
                    metadata = args['extra']['metadata']

            result = _update_submission(submission, status, job.id, traceback, metadata)
        except Exception as e:
            logger.exception("Failed to update submission (job_id=%s, submission_id=%s, status=%s)",
                             job.id, submission_id, status)
            raise SubmissionUpdateException(submission, e)
        return JobTaskResult(status=result)

    run_job_task(job_id, update_it, handle_update_exception)


@task(queue='site-worker', soft_time_limit=60 * 60 * 1)
def re_run_all_submissions_in_phase(phase_pk):
    phase = CompetitionPhase.objects.get(id=phase_pk)

    # Remove duplicate submissions this ugly way because MySQL distinct doesn't work...
    submissions_with_duplicates = CompetitionSubmission.objects.filter(phase=phase)
    submissions_without_duplicates = []
    file_names_seen = []

    for submission in submissions_with_duplicates:
        if submission.file.name not in file_names_seen:
            if settings.USE_AWS:
                file_names_seen.append(submission.s3_file)
            else:
                file_names_seen.append(submission.file.name)
            submissions_without_duplicates.append(submission)

    for submission in submissions_without_duplicates:
        if settings.USE_AWS:
            file_kwarg = {'s3_file': submission.s3_file}
        else:
            file_kwarg = {'file': submission.file}

        new_submission = CompetitionSubmission(
            participant=submission.participant,
            phase=submission.phase,
            docker_image=submission.docker_image,
            **file_kwarg
        )
        new_submission.save(ignore_submission_limits=True)

        evaluate_submission.apply_async((new_submission.pk, submission.phase.is_scoring_only))


@task(queue='site-worker')
def evaluate_submission(submission_id, is_scoring_only):
    """
    Starts the process of evaluating a user's submission to a competition.

    submission_id: The ID of the CompetitionSubmission object.
    is_scoring_only: True to skip the prediction step.

    Returns a Job object which can be used to track the progress of the operation.
    """
    task_args = {'submission_id': submission_id, 'predict': (not is_scoring_only)}
    job = Job.objects.create_job('evaluate_submission', task_args)
    job_id = job.pk

    logger.debug("evaluate_submission begins (job_id=%s)", job_id)
    submission_id = task_args['submission_id']
    logger.debug("evaluate_submission submission_id=%s (job_id=%s)", submission_id, job_id)
    predict_and_score = task_args['predict'] == True
    logger.debug("evaluate_submission predict_and_score=%s (job_id=%s)", predict_and_score, job_id)
    submission = CompetitionSubmission.objects.get(pk=submission_id)

    task_name, task_func = ('prediction', predict) if predict_and_score else ('scoring', score)
    try:
        logger.debug("evaluate_submission dispatching %s task (submission_id=%s, job_id=%s)",
                    task_name, submission_id, job_id)
        task_func(submission, job_id)
        logger.debug("evaluate_submission dispatched %s task (submission_id=%s, job_id=%s)",
                    task_name, submission_id, job_id)
    except Exception:
        logger.exception("evaluate_submission dispatch failed (job_id=%s, submission_id=%s)",
                         job_id, submission_id)
        update_submission.apply_async((job_id, {'status': 'failed'}, submission.secret))
    logger.debug("evaluate_submission ends (job_id=%s)", job_id)


def _send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None,
                        connection=None):
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently
    )

    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)

    return connection.send_messages(messages)


@task(queue='site-worker')
def send_mass_email(competition_pk, body=None, subject=None, from_email=None, to_emails=None):
    competition = Competition.objects.get(pk=competition_pk)
    context = Context({"competition": competition, "body": body, "site": Site.objects.get_current()})
    text = render_to_string("emails/notifications/participation_organizer_direct_email.txt", context)
    html = render_to_string("emails/notifications/participation_organizer_direct_email.html", context)

    mail_tuples = ((subject, text, html, from_email, [e]) for e in to_emails)

    _send_mass_html_mail(mail_tuples)


@task(queue='site-worker')
def do_chahub_retries():
    if not settings.CHAHUB_API_URL:
        return

    logger.info("Checking for objects needing to be re-sent to ChaHub")
    chahub_models = inheritors(ChaHubSaveMixin)
    for model in chahub_models:
        needs_retry = model.objects.filter(chahub_needs_retry=True)
        for instance in needs_retry:
            # Saving forces chahub update
            instance.save()


@task(queue='site-worker')
def do_phase_migrations():
    logger.info("Checking {} competitions for phase migrations.".format(len(competitions)))
    competitions = Competition.objects.filter(is_migrating=False)
    for c in competitions:
        c.check_future_phase_sumbmissions()


@task(queue='site-worker', soft_time_limit=60 * 60 * 24)
def make_modified_bundle(competition_pk, exclude_datasets_flag):
    # The following lines help dump this in a nice format
    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

    def dict_representer(dumper, data):
        return dumper.represent_dict(data.iteritems())

    def dict_constructor(loader, node):
        return OrderedDict(loader.construct_pairs(node))
    # Credit to miracle2k on Github for orderdict safe dump

    def represent_odict(dump, tag, mapping, flow_style=None):
        """Like BaseRepresenter.represent_mapping, but does not issue the sort().
        """
        value = []
        node = yaml.MappingNode(tag, value, flow_style=flow_style)
        if dump.alias_key is not None:
            dump.represented_objects[dump.alias_key] = node
        best_style = True
        if hasattr(mapping, 'items'):
            mapping = mapping.items()
        for item_key, item_value in mapping:
            node_key = dump.represent_data(item_key)
            node_value = dump.represent_data(item_value)
            if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
                best_style = False
            if not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if dump.default_flow_style is not None:
                node.flow_style = dump.default_flow_style
            else:
                node.flow_style = best_style
        return node
    yaml.SafeDumper.add_representer(OrderedDict,
                                    lambda dumper, value: represent_odict(dumper, u'tag:yaml.org,2002:map', value))
    # Following line supresses the broadexception warning. We catch and do a traceback for now from logs.
    # noinspection PyBroadException
    try:
        yaml.add_representer(unicode, SafeRepresenter.represent_unicode)
        yaml.add_representer(OrderedDict, dict_representer)
        yaml.add_constructor(_mapping_tag, dict_constructor)

        competition = models.Competition.objects.get(pk=competition_pk)
        logger.info("Creating Competion dump")
        temp_comp_dump = CompetitionDump.objects.create(competition=competition)
        yaml_data = OrderedDict()
        yaml_data['title'] = competition.title
        yaml_data['description'] = competition.description.replace("/n", "").replace("\"", "").strip()
        if competition.competition_docker_image and competition.competition_docker_image != "":
            yaml_data['competition_docker_image'] = competition.competition_docker_image
        if competition.image:
            yaml_data['image'] = 'logo.png'
        else:
            logger.info("No image for competition.")
        yaml_data['has_registration'] = competition.has_registration
        yaml_data['html'] = dict()
        yaml_data['phases'] = {}
        comp_su_list = ""
        temp_comp_dump.status = "Adding admins"
        temp_comp_dump.save()
        for su in competition.admins.all():
            logger.info("Adding admin")
            comp_su_list = comp_su_list + su.username + ","
        yaml_data['admin_names'] = comp_su_list
        temp_comp_dump.status = "Adding end-date"
        temp_comp_dump.save()
        logger.info("Adding end-date")
        if competition.end_date is not None:
            yaml_data['end_date'] = competition.end_date
        zip_buffer = StringIO.StringIO()
        zip_name = "{0}.zip".format(competition.title)
        zip_file = zipfile.ZipFile(zip_buffer, "w")
        for p in competition.pagecontent.pages.all():
            temp_comp_dump.status = "Adding {}.html".format(p.codename)
            temp_comp_dump.save()
            logger.info("Adding HTML")
            if p.codename in yaml_data["html"].keys() or p.codename == 'terms_and_conditions' or p.codename == 'get_data' or p.codename == 'submit_results':
                if p.codename == 'terms_and_conditions':
                    # overwrite this for consistency
                    p.codename = 'terms'
                    yaml_data['html'][p.codename] = p.codename + '.html'
                    zip_file.writestr(yaml_data["html"][p.codename], p.html.encode("utf-8"))
                if p.codename == 'get_data':
                    # overwrite for consistency
                    p.codename = 'data'
                    yaml_data['html'][p.codename] = p.codename + '.html'
                    zip_file.writestr(yaml_data["html"][p.codename], p.html.encode("utf-8"))
                # Do not include submit_results.
                if p.codename == 'submit_results':
                    pass
            else:
                yaml_data['html'][p.codename] = p.codename + '.html'
                zip_file.writestr(yaml_data["html"][p.codename], p.html.encode("utf-8"))
        file_cache = {}
        for index, phase in enumerate(competition.phases.all()):
            temp_comp_dump.status = "Adding phase {0}".format(phase.phasenumber)
            temp_comp_dump.save()
            logger.info("Adding phase")
            phase_dict = dict()
            phase_dict['phasenumber'] = phase.phasenumber
            phase_dict['label'] = phase.label
            phase_dict['start_date'] = phase.start_date
            phase_dict['max_submissions'] = phase.max_submissions
            phase_dict['color'] = phase.color
            phase_dict['max_submissions_per_day'] = phase.max_submissions_per_day
            # Write the programs/data to zip
            data_types = ['reference_data', 'scoring_program', 'input_data', 'starting_kit', 'public_data', 'ingestion_program']
            # data_types = []
            try:
                for data_type in data_types:
                    logger.info("Current data type is {}".format(data_type))
                    if hasattr(phase, data_type):
                        data_field = getattr(phase, data_type)
                        if data_field:
                            if data_field.file.name not in file_cache.keys():
                                if exclude_datasets_flag:
                                    data_field = getattr(phase, data_type + '_organizer_dataset')
                                    phase_dict[data_type] = data_field.key
                                    file_name = "{}_{}.zip".format(data_type, phase.phasenumber)
                                    file_cache[data_field.name] = {
                                        'name': file_name
                                    }
                                else:
                                    # logger.info("Datafield is {}".format(data_field))
                                    file_name = "{}_{}.zip".format(data_type, phase.phasenumber)
                                    phase_dict[data_type] = file_name
                                    file_cache[data_field.file.name] = {
                                        'name': file_name
                                    }
                                    zip_file.writestr(file_name, data_field.read())
                            else:
                                if exclude_datasets_flag:
                                    data_field = getattr(phase, data_type + '_organizer_dataset')
                                    # file_name = file_cache[data_field.name]['name']
                                    phase_dict[data_type] = data_field.key
                                else:
                                    file_name = file_cache[str(data_field.name)]['name']
                                    phase_dict[data_type] = file_name
            except ValueError:
                logger.info("Failed to retrieve the file.")
            datasets = phase.datasets.all()
            if datasets:
                phase_dict['datasets'] = dict()
                temp_comp_dump.status = "Adding datasets"
                temp_comp_dump.save()
                logger.info("Adding dataset")
                for data_set_index, data_set in enumerate(datasets):
                    phase_dict['datasets'][data_set_index] = {
                        'name': data_set.datafile.name,
                        'url': data_set.datafile.source_url,
                        'description': data_set.description
                    }
            yaml_data['phases'][index] = phase_dict
        yaml_data["leaderboard"] = dict()
        logger.info("Adding leaderboard.")
        leaderboards_dict = dict()
        columns_dictionary = dict()
        for index, submission_result_group in enumerate(SubmissionResultGroup.objects.filter(competition=competition)):
            logger.info("Adding a submission result group.")
            result_group = submission_result_group
            result_group_key = result_group.key
            leaderboards_dict[result_group_key] = {
                'label': submission_result_group.label,
                'rank': submission_result_group.ordering,
            }
            for index_score_def, submission_score_def_group in enumerate(SubmissionScoreDefGroup.objects.filter(group=submission_result_group)):
                logger.info("Adding a submission score def group.")
                score_def = submission_score_def_group.scoredef
                score_def_key = score_def.key
                columns_dictionary[score_def_key] = {
                    'leaderboard': leaderboards_dict[submission_result_group.label],
                    'label': score_def.label,
                    'rank': score_def.ordering,
                    'sort': score_def.sorting,
                }
        logger.info("YAML finalizing")
        yaml_data["leaderboard"]['leaderboards'] = leaderboards_dict
        yaml_data["leaderboard"]['columns'] = columns_dictionary
        logger.info("Done with leaderboard")
        temp_comp_dump.status = "Finalizing"
        temp_comp_dump.save()
        logger.info("Finalizing")
        comp_yaml_my_dump = yaml.safe_dump(yaml_data, default_flow_style=False, allow_unicode=True, encoding="utf-8")
        if competition.image:
            zip_file.writestr(yaml_data["image"], competition.image.file.read())
        else:
            logger.info("No image for competition.")
        zip_file.writestr("competition.yaml", comp_yaml_my_dump)
        zip_file.close()
        logger.info("Stored Zip buffer yaml dump, and image")
        logger.info("Attempting to save ZIP")
        temp_comp_data = ContentFile(zip_buffer.getvalue())
        save_success = False
        while not save_success:
            counter = 0
            logger.info("Attempting to save new object.")
            try:
                temp_comp_dump.data_file.save(zip_name, temp_comp_data)
                save_success = True
            except SoftTimeLimitExceeded:
                logger.info("Failed to save object, retrying.")
                counter += 1
                continue
            if counter == 5:
                temp_comp_dump.status = "Failed"
                temp_comp_dump.save()
                logger.info("Failed to save object after 5 tries. Stopping.")
                save_success = True
        logger.info("Saved zip file to Competition dump")
        temp_comp_dump.status = "Finished"
        temp_comp_dump.save()
        logger.info("Set status to finished")
    except:
        logger.info("There was an error making a Competition dump")
        logger.info(traceback.format_exc())
        temp_comp_dump.status = "Failed"
        temp_comp_dump.save()
