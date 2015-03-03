from django.db import models
from django.contrib.auth import models as auth_models


class ClUser(auth_models.AbstractUser):
    participation_status_updates = models.BooleanField(default=True)
    organizer_status_updates = models.BooleanField(default=True)
    organizer_direct_message_updates = models.BooleanField(default=True)

    organization_or_affiliation = models.CharField(max_length=255, null=True, blank=True)

    team_name = models.CharField(max_length=64, null=True, blank=True)
    team_members = models.TextField(null=True, blank=True)
