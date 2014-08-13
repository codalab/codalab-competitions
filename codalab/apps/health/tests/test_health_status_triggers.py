import datetime
import mock

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.health.models import HealthSettings

User = get_user_model()


class HealthStatusTriggerTests(TestCase):
    def setUp(self):
        self.health_settings = HealthSettings.objects.get_or_create(pk=1)[0]
        self.health_settings.emails = "test@test.com, test2@test.com"

    def test_health_status_triggers_when_jobs_in_queue_greater_than_100(self):
        pass

    def test_health_status_triggers_when_a_job_takes_greater_than_10_minutes_to_process(self):
        pass

    def test_health_status_triggers_sends_to_emails_comma_separated(self):
        pass
