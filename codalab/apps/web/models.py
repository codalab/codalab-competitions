from django.db import models
from django.conf import settings
from publish.models import Publishable


class ExternalFileType(models.Model):
    name = models.CharField(max_length=20)
    code = models.SlugField(max_length=20)

    def __unicode__(self):
        return self.name

class ExternalFile(models.Model):
    type = models.ForeignKey(ExternalFileType)
    source_url = models.URLField()
    source_address_info = models.CharField(max_length=200, blank=True)

class ParticipantStatus(models.Model):
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30)
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class TabVisibility(models.Model):
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name 

class Competition(Publishable):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    has_registration = models.BooleanField(default=False)
    end_date = models.DateField(null=True,blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_creator')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_modified_by')
    last_modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('is_owner', 'Owner'),
            ('can_edit', 'Edit'),
            )

    def __unicode__(self):
        return self.title

class CompetitionPhase(Publishable):
    competition = models.ForeignKey(Competition)
    phasenumber = models.PositiveIntegerField()
    label = models.CharField(max_length=50,blank=True)
    start_date = models.DateTimeField()
    max_submissions = models.PositiveIntegerField(default=100)
    manifest_file_id = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.phasenumber)

class CompetitionParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    competition = models.ForeignKey(Competition,related_name='participation')
    status = models.ForeignKey(ParticipantStatus)
    reason = models.CharField(max_length=100,null=True,blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.user.username)

class CompetitionWizard(models.Model):
    competition = models.ForeignKey(Competition)
    step = models.IntegerField(default=1)
    title = models.CharField(max_length=100,null=True,blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    description = models.TextField(null=True,blank=True)
    public = models.BooleanField(default=False)
    saveflag = models.BooleanField(default=True)
    image_url = models.URLField(null=True,blank=True)
    
    class Meta:
        unique_together = (('competition','step'),)
         
    def __unicode__(self):
        return "%s step %d" % (self.competition,self.step)



class CompetitionDataset(Publishable):
    competition = models.ForeignKey(Competition)
    number = models.PositiveIntegerField(default=0)
    dataset = models.ForeignKey(ExternalFile)
    

# Bundle Model
class Bundle(models.Model):
  title = models.CharField(max_length=100,null=True,blank=True)
  created = models.DateTimeField(auto_now_add=True)
  #submitter = models.ForeignKey(User)
  url = models.URLField("URL", max_length=250, blank=True)
  description = models.TextField(blank=True)
    
  def __unicode__(self):
    return self.name