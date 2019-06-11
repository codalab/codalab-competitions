from django.db import models


class HealthSettings(models.Model):
    """Base Health Settings Model. Counts the amount of jobs ready to process."""
    emails = models.TextField(null=True, blank=True)
    threshold = models.PositiveIntegerField(default=25, null=True, blank=True)
    congestion_threshold = models.PositiveIntegerField(default=100, null=True, blank=True)


class Worker(models.Model):
    ip = models.TextField(max_length=24)
    cpu_count = models.PositiveIntegerField()
    mem_mb = models.PositiveIntegerField()
    harddrive_gb = models.PositiveIntegerField()
    gpus = models.PositiveIntegerField(default=0)


class TaskMetadata(models.Model):
    worker = models.ForeignKey(Worker, related_name="tasks")
    submission = models.ForeignKey('web.CompetitionSubmission', related_name="tasks")
    is_prediction = models.BooleanField()
    is_scoring = models.BooleanField()
    start = models.TimeField()
    end = models.TimeField()
