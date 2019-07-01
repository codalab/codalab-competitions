from django.db import models


class HealthSettings(models.Model):
    """Base Health Settings Model. Counts the amount of jobs ready to process."""
    emails = models.TextField(null=True, blank=True)
    threshold = models.PositiveIntegerField(default=25, null=True, blank=True)
    congestion_threshold = models.PositiveIntegerField(default=100, null=True, blank=True)


class Worker(models.Model):
    unique_id = models.UUIDField()
    ip = models.TextField(max_length=24)
    cpu_count = models.PositiveIntegerField()
    mem_mb = models.PositiveIntegerField()
    harddrive_gb = models.PositiveIntegerField()
    gpus = models.PositiveIntegerField(default=0)
    queue = models.ForeignKey('queues.Queue', null=True, blank=True)

    def __str__(self):
        return "{} {}x cpu {}MB mem {}GB hdd {}x gpus '{}' queue".format(
            self.ip,
            self.cpu_count,
            self.mem_mb,
            self.harddrive_gb,
            self.gpus,
            self.queue.name if self.queue else 'default'
        )


class TaskMetadata(models.Model):
    worker = models.ForeignKey(Worker, related_name="tasks")
    submission = models.ForeignKey('web.CompetitionSubmission', related_name="tasks")
    is_predicting = models.BooleanField(default=False)
    is_scoring = models.BooleanField(default=False)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        prediction_or_scoring = "Scoring" if self.is_scoring else "Predicting"
        return "{} sub = '{}', started = '{}', ended = '{}'".format(
            prediction_or_scoring,
            self.submission_id,
            self.start or '',
            self.end or ''
        )
