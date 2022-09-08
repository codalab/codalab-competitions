from django.db import models


class HealthSettings(models.Model):
    """Base Health Settings Model. Counts the amount of jobs ready to process."""
    emails = models.TextField(null=True, blank=True)
    threshold = models.PositiveIntegerField(default=25, null=True, blank=True)
    congestion_threshold = models.PositiveIntegerField(default=100, null=True, blank=True)


class CompetitionStorageDataPoint(models.Model):
    competition_id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    creator = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    submissions = models.BigIntegerField(default=0)
    datasets = models.BigIntegerField(default=0)
    dumps = models.BigIntegerField(default=0)
    bundle = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)


class StorageSnapshot(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    bucket_name = models.CharField(max_length=255)
    total_use = models.BigIntegerField(default=0)


class StorageUsageHistory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    bucket_name = models.CharField(max_length=255)
    at_date = models.DateTimeField()
    usage = models.BigIntegerField(default=0)


class UserStorageDataPoint(models.Model):
    user_id = models.PositiveIntegerField(primary_key=True)
    email = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    competitions_total = models.BigIntegerField(default=0)
    datasets_total = models.BigIntegerField(default=0)
    submissions_total = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)
