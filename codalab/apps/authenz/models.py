from django.db import models
from django.contrib.auth import models as auth_models


class ClUser(auth_models.AbstractUser):
    participation_status_updates = models.BooleanField(default=True)
    organizer_status_updates = models.BooleanField(default=True)
    organizer_direct_message_updates = models.BooleanField(default=True)

