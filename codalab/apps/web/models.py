from django.db import models
from django.conf import settings
import reversion


class CompetitionDeploymentState(models.Model):
    name = models.CharField(max_length=30)
    codename = models.SlugField(max_length=30)
    
    def __unicode__(self):
        return self.name

class ParticipationStatus(models.Model):
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

class TabVisibility(models.Model):
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name 

class Competition(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    has_registration = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    has_edits = models.BooleanField(default=False)
    end_date = models.DateField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_creator')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_modified_by')
    last_modified = models.DateTimeField()


    def __unicode__(self):
        return self.title

