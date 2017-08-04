import os
from django.db import models
from django.contrib.auth import models as auth_models
from django.utils.functional import cached_property
from apps.web.utils import PublicStorage

class ClUser(auth_models.AbstractUser):
    """
    Base User model
    """
    # Notification settings
    participation_status_updates = models.BooleanField(default=True)
    organizer_status_updates = models.BooleanField(default=True)
    organizer_direct_message_updates = models.BooleanField(default=True)
    email_on_submission_finished_successfully = models.BooleanField(default=False)

    # Profile image
    image = models.FileField(upload_to='user_photo', storage=PublicStorage, null=True, blank=True, verbose_name="Logo")
    image_url_base = models.CharField(max_length=255, null=True, blank=True)

    # Profile details
    organization_or_affiliation = models.CharField(max_length=255, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    webpage = models.URLField(null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    ORCID = models.CharField(max_length=255, null=True, blank=True)

    team_name = models.CharField(max_length=64, null=True, blank=True)
    team_members = models.TextField(null=True, blank=True)

    method_name = models.CharField(max_length=20, null=True, blank=True)
    method_description = models.TextField(null=True, blank=True)
    project_url = models.URLField(null=True, blank=True)
    publication_url = models.URLField(null=True, blank=True)
    bibtex = models.TextField(null=True, blank=True)

    contact_email = models.EmailField(null=True, blank=True)

    # Allow the user to decide if the profile is public or not
    public_profile = models.BooleanField(default=False)

    def update_filename(instance, filename):
        path = "user_photo"
        img_format = "{0}{1}".format(instance.username, instance.file_extension)
        return os.path.join(path, img_format)

    def save(self, *args, **kwargs):
        # Make sure the image_url_base is set from the actual storage implementation
        self.image_url_base = self.image.storage.url('')

        # Do the real save
        return super(ClUser, self).save(*args, **kwargs)

    @cached_property
    def image_url(self):
        # Return the transformed image_url
        if self.image:
            return os.path.join(self.image_url_base, self.image.name)
        return None

    rabbitmq_queue_limit = models.PositiveIntegerField(default=5, blank=True)
    rabbitmq_username = models.CharField(max_length=36, null=True, blank=True)
    rabbitmq_password = models.CharField(max_length=36, null=True, blank=True)

