from django.conf import settings
from django.db import models
from django_extensions.db.fields import UUIDField


class Queue(models.Model):
    name = models.CharField(max_length=64)
    vhost = UUIDField()
    is_public = models.BooleanField(default=False)
    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='organizers',
        blank=True,
        null=True,
        help_text="(Organizers allowed to view this queue when they assign their competition to a queue)"
    )
