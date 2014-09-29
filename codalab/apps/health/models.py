from django.db import models


class HealthSettings(models.Model):
    emails = models.TextField(null=True, blank=True)
