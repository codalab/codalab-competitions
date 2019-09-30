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
        five_days_ago = timezone.now() - datetime.timedelta(days=5)
        with patch.object(timezone, 'now', return_value=five_days_ago):
            TaskResult.objects.create(task_id=str(uuid.uuid4()))
        # Create a task result at present time
        TaskResult.objects.create(task_id=str(uuid.uuid4()))
        assert TaskResult.objects.count() == 2
        periodic_task_result_removal()
        assert TaskResult.objects.count() == 1
