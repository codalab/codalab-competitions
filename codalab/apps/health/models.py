from django.db import models


class HealthSettings(models.Model):
    emails = models.TextField(null=True, blank=True)
    threshold = models.PositiveIntegerField(default=25, null=True, blank=True)
