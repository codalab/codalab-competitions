from django.db import models
from django.contrib.auth.models import User

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

class CompetitionInfo(models.Model):
    competition = models.ForeignKey('Competition')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=4000, null=True, blank=True)
    image_url = models.URLField()
    end_date = models.DateField()
    creator = models.ForeignKey(User, related_name='competitioninfo_creator')
    modified_by = models.ForeignKey(User, related_name='competitioninfo_modified_by')
    last_modified = models.DateTimeField()

    def __unicode__(self):
        return self.title

class Competition(models.Model):
    has_registration = models.BooleanField(default=False)
    info = models.ForeignKey(CompetitionInfo, related_name='competition_info',
                             null=True,blank=True)
    staged_info = models.ForeignKey(CompetitionInfo, 
                                    related_name='competition_staged_info',
                                    null=True,blank=True)
    is_public = models.BooleanField(default=False)
    has_edits = models.BooleanField(default=False)

    def __unicode__(self):
        return "Competition %s" % str(self.pk)

