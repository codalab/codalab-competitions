"""
Defines models for this Django app.
"""
import json
import logging
import threading

from codalabtools.azure_extensions import AzureServiceBusQueue
from django.conf import settings
from django.db import (models,
                       transaction)

logger = logging.getLogger(__name__)

# Queues

_lock = threading.Lock()
_queues = {}

def getQueue(name=None):
    """
    Returns a Queue given its name.
    """
    if name is None:
        name = "_default_site_queue"
    if name in _queues:
        return _queues[name]

    queue = None
    with _lock:
        if name == "_default_site_queue":
            queue = AzureServiceBusQueue(settings.SBS_NAMESPACE,
                                         settings.SBS_ACCOUNT_KEY,
                                         settings.SBS_ISSUER,
                                         settings.SBS_RESPONSE_QUEUE)
            _queues[name] = queue

    return queue

# Jobs

class JobManager(models.Manager):
    """
    Adds job-specific convenience methods to the default Django Manager.
    """

    def create_job(self, task_type, task_args):
        """
        Creates a job.

        task_type: A string identifying the type of task to carry out.
        task_args: An object defining the task's input arguments. The object must allow
        serialization to a JSON string using `json.dumps(obj)`. A None value is acceptable
        if the task requires no input arguments.
        """
        task_args_json = "" if task_args is None else json.dumps(task_args)
        job = self.create(task_type=task_type, task_args_json=task_args_json)
        return job

    def create_and_dispatch_job(self, task_type, task_args, queue_name=None):
        """
        Creates a job and dispatches it to the specified queue.

        task_type: A string identifying the type of task to carry out.
        task_args: An object defining the task's input arguments. The object must allow
        serialization to a JSON string using `json.dumps(obj)`. A None value is acceptable
        if the task requires no input arguments.
        queue_name: The name of the target Queue. If name is None, the queue connected to
        the site workers is used.
        """
        job = self.create_job(task_type, task_args)
        getQueue(queue_name).send_message(job.create_json_message())
        return job

class Job(models.Model):
    """
    Defines a job which will carry out a long running task.
    """

    # Possible status codes
    PENDING = 0
    RUNNING = 1
    FINISHED = 2
    FAILED = 3
    # Status friendly code and display text
    STATUS_BY_CODE = {
        PENDING: { 'code_name':'pending', 'display_text': 'Pending' },
        RUNNING: { 'code_name':'running', 'display_text': 'Running' },
        FINISHED: { 'code_name':'finished', 'display_text': 'Finished' },
        FAILED: { 'code_name':'failed', 'display_text': 'Failed' }
    }
    # Reverse map to get integer code from friendly code name
    STATUS_BY_CODE_NAME = { v['code_name']: k  for (k, v) in STATUS_BY_CODE.items() }

    created = models.DateTimeField('Date of creation', auto_now_add=True)
    updated = models.DateTimeField('Date of last update', auto_now=True)
    status = models.PositiveIntegerField('Status', default=PENDING, db_index=True)
    task_type = models.CharField('Task type', max_length=256)
    task_args_json = models.TextField('JSON-encoded task arguments', blank=True)

    objects = JobManager()

    def __unicode__(self):
        return "Job(pk={0})".format(self.pk)

    def can_transition_to(self, new_status):
        """
        Validates that the transition from the job's current status to the given new status is valid.
        """
        if new_status in Job.STATUS_BY_CODE:
            if self.status == Job.FINISHED:
                return False
            if self.status == Job.FAILED:
                return False
            if self.status == Job.PENDING:
                return new_status != Job.PENDING
            if self.status == Job.RUNNING:
                return (new_status == Job.FINISHED) or (new_status == Job.FAILED)
        else:
            return False

    def create_json_message(self):
        """
        Gets the JSON-encoded message to describe the given job to a worker.
        """
        data = { "id": self.pk, "task_type": self.task_type }
        if len(self.task_args_json) > 0:
            data['task_args'] = json.loads(self.task_args_json)
        return json.dumps(data)

#
# Tasks
#

def update_job_status_task(job_id, args):
    """
    A task to update the status of a Job instance.

    job_id: The ID of the job to update.
    args: A dictionary with the arguments for the task. Expected items are:
        args['status']: friendly code name of the new status
    """
    status_code_name = args['status']
    logger.debug("Starting request to update job (id=%s) with new status name=%s", job_id, status_code_name)
    status = Job.STATUS_BY_CODE_NAME[status_code_name]
    with transaction.commit_on_success():
        job = Job.objects.select_for_update().get(pk=job_id)
        if job.can_transition_to(status):
            job.status = status
            job.save()
            logger.info("Completed update for job id=%s. New status=%s.", job_id, job.status)
        else:
            logger.info("Skipping update for job id=%s: invalid transition %s -> %s.", job_id, job.status, status)

def run_job_task(job_id, computation):
    """
    Runs the task associated with a job. If the computation succeeds (runs to completion without
    raising an exception), then the job status is updated with the status code returned by the
    computation, but if the computation fails then the job status is set to Failed.

    job_id: The ID of the job.
    computation: The function invoked to run the task: new_status_code = computation(job).
    """
    logger.debug("Entering run_job_task (job_id=%s).", job_id)
    try:
        job = Job.objects.get(pk=job_id)
        new_status = computation(job)
        logger.debug("Task execution succeeded (job_id=%s, new_status=%s).", job_id, new_status)
        update_job_status_task(job_id, { 'status': Job.STATUS_BY_CODE[new_status]['code_name'] })
    except:
        logger.exception("An error occurred during task execution (job_id=%s).", job_id)
        update_job_status_task(job_id, { 'status': Job.STATUS_BY_CODE[Job.FAILED]['code_name'] })

# DbMessage, DbMessageQueue
# DbMessage.objects.filter(read=False).order_by('pk')[0:1].get()
#    @staticmethod
#    def _get_next_dbmessage():
#        """
#        Gets the next message from the DbMessageQueue.
#        """
#        msg = None
#        try:
#            msg = DbMessage.objects.filter(read=False).order_by('pk')[0:1].get()
#        except DbMessage.DoesNotExist:
#            pass
#        except:
#            traceback.print_exc()
#        return msg
