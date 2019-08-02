from urlparse import urlparse

from django.conf import settings
from django.db import models
from pyrabbit.http import HTTPError
# from django.contrib.sites.models import Site

import uuid

from apps.queues import rabbit


class Queue(models.Model):
    name = models.CharField(max_length=64)
    vhost = models.UUIDField(unique=True)
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='organizers',
        blank=True,
        help_text="(Organizers allowed to view this queue when they assign their competition to a queue)"
    )

    def __str__(self):
        return self.name

    @property
    def broker_url(self):
        # Start with pyamqp://guest:guest@localhost:5672//
        broker_url_parts = urlparse(settings.BROKER_URL)
        # Get localhost:5672
        from django.contrib.sites.models import Site
        host = Site.objects.get_current().domain

        return "pyamqp://{}:{}@{}/{}".format(
            self.owner.rabbitmq_username,
            self.owner.rabbitmq_password,
            host,
            self.vhost
        )

    def delete(self, using=None):
        try:
            rabbit.delete_vhost(str(self.vhost))
        except HTTPError:
            # Vhost not found or something
            pass
        return super(Queue, self).delete(using)
