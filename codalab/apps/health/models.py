from django.db import models
from django.urls import reverse
from django.utils.timezone import now


class HealthSettings(models.Model):
    """Base Health Settings Model. Counts the amount of jobs ready to process."""
    emails = models.TextField(null=True, blank=True)
    threshold = models.PositiveIntegerField(default=25, null=True, blank=True)
    congestion_threshold = models.PositiveIntegerField(default=100, null=True, blank=True)


class Worker(models.Model):
    unique_id = models.UUIDField()
    ip = models.TextField(max_length=24, null=True, blank=True)
    cpu_count = models.PositiveIntegerField(null=True, blank=True)
    mem_mb = models.PositiveIntegerField(null=True, blank=True)
    harddrive_gb = models.PositiveIntegerField(null=True, blank=True)
    gpus = models.PositiveIntegerField(default=0, null=True, blank=True)
    queue = models.ForeignKey('queues.Queue', null=True, blank=True)
    last_keep_alive = models.DateTimeField(default=now, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} {}x cpu {}MB mem {}GB hdd {}x gpus '{}' queue".format(
            self.ip,
            self.cpu_count,
            self.mem_mb,
            self.harddrive_gb,
            self.gpus,
            self.queue.name if self.queue else 'default'
        )

    def get_absolute_url(self):
        return reverse('health_worker_detail', args=(self.pk,))


class WorkerStateChange(models.Model):
    worker = models.ForeignKey(Worker)
    up = models.BooleanField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return "{} -- Worker = '{}' is {}".format(
            self.timestamp.strftime("%b %d %H:%M:%S"),
            self.worker.unique_id,
            "up" if self.up else "down",
        )


class TaskMetadata(models.Model):
    worker = models.ForeignKey(Worker, null=True, blank=True, related_name="tasks")
    submission = models.ForeignKey('web.CompetitionSubmission', related_name="tasks")
    is_predicting = models.BooleanField(default=True)
    is_scoring = models.BooleanField(default=False)
    queued = models.DateTimeField(default=now)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    failed_to_complete = models.BooleanField(default=False)

    def __str__(self):
        prediction_or_scoring = "Scoring" if self.is_scoring else "Predicting"
        return "{} sub = '{}', started = '{}', ended = '{}'".format(
            prediction_or_scoring,
            self.submission_id,
            self.start or '',
            self.end or ''
        )
