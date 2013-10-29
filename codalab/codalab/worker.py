#!/usr/bin/env python
"""
Defines the worker process which handles background tasks for the web site.
"""
import logging
import os
import sys
import time
from os.path import dirname, abspath, basename

# Add codalab site directory to the module search path
sys.path.append(dirname(dirname(abspath(__file__))))

# Django configuration
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")
from configurations import importer
importer.install()

from codalabtools import BaseWorker
from apps.jobs.models import (update_job_status_task,
                              getQueue,
                              Job)
from apps.web.tasks import (echo_task,
                            create_competition_task,
                            evaluate_submission_task,
                            update_submission_task)

logger = logging.getLogger('codalab')

def start_worker():
    """
    Setup the worker and start it.
    """
    queue = getQueue()
    vtable = {
        'status_update': update_job_status_task,
        'echo': echo_task,
        'create_competition': create_competition_task,
        'evaluate_submission': evaluate_submission_task,
        'run_update': update_submission_task
    }
    worker = BaseWorker(queue, vtable, logger)
    logger.info("Starting site worker.")
    worker.start()

def start_producer():
    """
    Start a sample task producer.
    """
    logger.info("Starting sample task producer.")
    cur_delay = 5
    max_delay = 60
    delay_inc = 5
    while True:
        time.sleep(cur_delay)
        job = Job.objects.create_and_dispatch_job('status_update', { 'status': 'finished' })
        logger.info("Created job with id=%s", job.id)
        if (cur_delay < max_delay):
            cur_delay += min(delay_inc, (max_delay - cur_delay))

if __name__ == "__main__":

    usage = """
Usage: %s [command]

command:
    worker (default): starts the site background worker.
    producer: starts a sample producer of tasks directed at the site background worker.
""" % basename(sys.argv[0])

    command = "worker"
    if len(sys.argv) > 1:
        command = sys.argv[1]

    if command == "worker":
        start_worker()
    if command == "producer":
        start_producer()
    else:
        print usage
        sys.exit(1)
