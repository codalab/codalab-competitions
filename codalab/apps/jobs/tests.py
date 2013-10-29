"""
Defines unit tests for this Django app.
"""
import json
import time

from django.test import TestCase
from django.utils import timezone

from apps.jobs import models
from apps.jobs.models import Job

class JobsTests(TestCase):
    """
    Tests for creating, updating and deleting jobs.
    """

    def test_basic_create_delete(self):
        """
        Test basic job creation and deletion.
        """
        now = timezone.now()
        time.sleep(0.001)
        job = Job.objects.create(task_type="foo")
        self.assertIsNotNone(job)
        self.assertGreaterEqual(job.created, now)
        self.assertGreaterEqual(job.updated, now)
        self.assertEqual(job.status, Job.PENDING)
        self.assertEqual(job.task_type, "foo")
        self.assertEqual(job.task_args_json, "")
        self.assertTrue(Job.objects.filter(pk=job.pk).exists())
        job.delete()
        self.assertFalse(Job.objects.filter(pk=job.pk).exists())

    def test_create_with_args(self):
        """
        Test basic job creation when required input is missing.
        """
        task_type = 'foo'
        task_args = { 'value1': 'a string', 'value2': 2, 'value3' : { 'key1' : 'val1' } }
        job = Job.objects.create_job(task_type, task_args)
        self.assertIsNotNone(job)
        self.assertEqual(job.task_type, task_type)
        self.assertTrue(len(job.task_args_json) > 0)
        task_args_back = json.loads(job.task_args_json)
        self.assertDictEqual(task_args, task_args_back)
        self.assertEqual('val1', task_args_back['value3']['key1'])

        json_msg = job.create_json_message()
        self.assertIsNotNone(json_msg)
        self.assertTrue(len(json_msg) > 0)
        msg = json.loads(json_msg)
        self.assertTrue('id' in msg)
        self.assertEqual(job.pk, msg['id'])
        self.assertTrue('task_type' in msg)
        self.assertEqual(task_type, msg['task_type'])
        self.assertTrue('task_args' in msg)
        self.assertDictEqual(task_args, msg['task_args'])

        self.assertTrue(Job.objects.filter(pk=job.pk).exists())
        job.delete()
        self.assertFalse(Job.objects.filter(pk=job.pk).exists())

    def test_status_update(self):
        """
        Test valid transitions for job status.
        """
        job = Job.objects.create(task_type="foo")
        self.assertIsNotNone(job)
        self.assertEqual(job.status, Job.PENDING)
        self.assertFalse(job.can_transition_to(Job.PENDING))
        self.assertTrue(job.can_transition_to(Job.RUNNING))
        self.assertTrue(job.can_transition_to(Job.FINISHED))
        self.assertTrue(job.can_transition_to(Job.FAILED))
        self.assertFalse(job.can_transition_to(123456789))

        job.status = Job.RUNNING
        self.assertEqual(job.status, Job.RUNNING)
        self.assertFalse(job.can_transition_to(Job.PENDING))
        self.assertFalse(job.can_transition_to(Job.RUNNING))
        self.assertTrue(job.can_transition_to(Job.FINISHED))
        self.assertTrue(job.can_transition_to(Job.FAILED))
        self.assertFalse(job.can_transition_to(123456789))

        job.status = Job.FINISHED
        self.assertEqual(job.status, Job.FINISHED)
        self.assertFalse(job.can_transition_to(Job.PENDING))
        self.assertFalse(job.can_transition_to(Job.RUNNING))
        self.assertFalse(job.can_transition_to(Job.FINISHED))
        self.assertFalse(job.can_transition_to(Job.FAILED))
        self.assertFalse(job.can_transition_to(123456789))

        job.status = Job.FAILED
        self.assertEqual(job.status, Job.FAILED)
        self.assertFalse(job.can_transition_to(Job.PENDING))
        self.assertFalse(job.can_transition_to(Job.RUNNING))
        self.assertFalse(job.can_transition_to(Job.FINISHED))
        self.assertFalse(job.can_transition_to(Job.FAILED))
        self.assertFalse(job.can_transition_to(123456789))

    def test_update_task(self):
        """
        Test local in-process execution.
        """
        def single_run(a_id, a_args):
            """
            Create a job status update task, run it, query for the job and return it.

            a_id: job ID
            a_args: job status update task arguments
            """
            models.update_job_status_task(a_id, a_args)
            return Job.objects.get(pk=job.id)

        def last_update_of(a_job):
            """
            Return a_job.update after a brief pause to ensure the test produces different timestamps with each update.

            a_job: A job instance
            """
            time.sleep(0.01)
            return a_job.updated

        job = Job.objects.create()
        self.assertEqual(job.status, Job.PENDING)
        self.assertIsNotNone(job)
        last_updated = last_update_of(job)
        # pending -> running
        job = single_run(job.id, { 'status': 'running' })
        self.assertEqual(job.status, Job.RUNNING)
        self.assertGreaterEqual(job.updated, last_updated)
        last_updated = last_update_of(job)
        # running -> finished
        job = single_run(job.id, { 'status': 'finished' })
        self.assertEqual(job.status, Job.FINISHED)
        self.assertGreaterEqual(job.updated, last_updated)
        last_updated = last_update_of(job)
        # Try finished -> running which is not valid and will have no effect
        job = single_run(job.id, { 'status': 'running' })
        self.assertEqual(job.status, Job.FINISHED)
        self.assertEqual(job.updated, last_updated)
        job.delete()
