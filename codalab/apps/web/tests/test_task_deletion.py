import datetime
import uuid

from django.test import TestCase
from django_celery_results.models import TaskResult
from django.utils import timezone

from apps.web.tasks import periodic_task_result_removal
from mock import patch


class CompetitionTaskRemovalTestCase(TestCase):

    def test_periodic_task_removes_stale_task_results(self):
        # Create a task result in the past
        old_task = None
        five_days_ago = timezone.now() - datetime.timedelta(days=5)
        with patch.object(timezone, 'now', return_value=five_days_ago):
            old_task = TaskResult.objects.create(task_id=str(uuid.uuid4()))

        # Create a task result at present time
        new_task = TaskResult.objects.create(task_id=str(uuid.uuid4()))

        assert TaskResult.objects.count() == 2

        periodic_task_result_removal()

        # Make sure current task is kept
        current_tasks = TaskResult.objects.all()
        assert len(current_tasks) == 1
        assert current_tasks[0].pk == new_task.pk

        # Confirm old was deleted
        assert not TaskResult.objects.filter(pk=old_task.pk).exists()
