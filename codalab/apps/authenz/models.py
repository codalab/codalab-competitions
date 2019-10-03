from django.db import models
from django.contrib.auth import models as auth_models

from apps.chahub.models import ChaHubSaveMixin


class ClUser(ChaHubSaveMixin, auth_models.AbstractUser):
    """
    Base User model
    """
    # Notification settings
    participation_status_updates = models.BooleanField(default=True)
    organizer_status_updates = models.BooleanField(default=True)
    organizer_direct_message_updates = models.BooleanField(default=True)
    email_on_submission_finished_successfully = models.BooleanField(default=False)

    # Profile details
    organization_or_affiliation = models.CharField(max_length=255, null=True, blank=True)

    team_name = models.CharField(max_length=64, null=True, blank=True)
    team_members = models.TextField(null=True, blank=True)

    method_name = models.CharField(max_length=20, null=True, blank=True)
    method_description = models.TextField(null=True, blank=True)
    project_url = models.URLField(null=True, blank=True)
    publication_url = models.URLField(null=True, blank=True)
    bibtex = models.TextField(null=True, blank=True)

    contact_email = models.EmailField(null=True, blank=True)

    rabbitmq_queue_limit = models.PositiveIntegerField(default=5, blank=True)
    rabbitmq_username = models.CharField(max_length=36, null=True, blank=True)
    rabbitmq_password = models.CharField(max_length=36, null=True, blank=True)

    def get_chahub_endpoint(self):
        return "profiles/"

    def get_chahub_data(self):
        data = {
            'email': self.email,
            'username': self.username,
            'remote_id': self.pk,
            'details': {
                "is_active": self.is_active,
                "last_login": str(self.last_login),
                "date_joined": str(self.date_joined),
            }
        }
        return [data]

    def get_chahub_is_valid(self):
        # By default, always push
        return True
