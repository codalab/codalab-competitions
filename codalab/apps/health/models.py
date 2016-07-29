from django.db import models


class HealthSettings(models.Model):
    """Base Health Settings Model. Counts the amount of jobs ready to process."""
    emails = models.TextField(null=True, blank=True)
    threshold = models.PositiveIntegerField(default=25, null=True, blank=True)
