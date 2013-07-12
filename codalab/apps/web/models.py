from django.db import models
from django.conf import settings
from publish.models import Publishable
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.text import slugify

class ContentVisibility(models.Model):
    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20,unique=True)
    classname = models.CharField(max_length=30,null=True,blank=True)

    def __unicode__(self):
        return self.name

class ContentContainerType(models.Model):
    name = models.CharField(max_length=50)
    codename = models.SlugField(max_length=50,unique=True)
    is_active = models.BooleanField(default=True)


    def __unicode__(self):
        return self.name

class ContentContainer(models.Model):
    name = models.CharField(max_length=30)
    type = models.ForeignKey(ContentContainerType, unique=True)

    def __unicode__(self):
        return "%s %s" % (self.name,self.type.name)

class ContentEntity(models.Model):
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True)
    container = models.ForeignKey(ContentContainer, related_name='entities')
    visibility = models.ForeignKey(ContentVisibility)
    label = models.CharField(max_length=50)
    codename = models.SlugField(max_length=81,null=True,blank=True)
    rank = models.IntegerField(default=0)
    max_items = models.IntegerField(default=1)

    class Meta:
        ordering = ['rank']
        unique_together = (('label','container'),)

    def __unicode__(self):
        return self.label

    def make_codename(self):
        return slugify("%s %s" % (self.container.type.codename, self.label))
    
    def save(self,*args,**kwargs):
        if not self.codename:
            self.codename = self.make_codename()
        return super(ContentEntity,self).save(*args,**kwargs)
    
    @property
    def toplevel(self):
        return self.parent is None

class PageContainer(models.Model):
    entity = models.ForeignKey(ContentEntity)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    owner = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('content_type','object_id'),)
    
class Page(Publishable):
    pagecontainer = models.ForeignKey(PageContainer,related_name='pages')
    rank = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=100, null=True, blank=True)
    visible = models.BooleanField(default=True)
    markup = models.TextField(blank=True)
    html = models.TextField(blank=True)
    

class ExternalFileType(models.Model):
    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20)

    def __unicode__(self):
        return self.name

class ExternalFile(models.Model):
    type = models.ForeignKey(ExternalFileType)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
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
    pagecontainer = generic.GenericRelation(PageContainer)
    

    class Meta:
        permissions = (
            ('is_owner', 'Owner'),
            ('can_edit', 'Edit'),
            )

    def __unicode__(self):
        return self.title

class CompetitionDataset(Publishable):
    competition = models.ForeignKey(Competition)
    number = models.PositiveIntegerField(default=0)
    datafile = models.ForeignKey(ExternalFile)

class CompetitionPhase(Publishable):
    competition = models.ForeignKey(Competition)
    phasenumber = models.PositiveIntegerField()
    label = models.CharField(max_length=50,blank=True)
    start_date = models.DateTimeField()
    max_submissions = models.PositiveIntegerField(default=100)
    dataset = models.ForeignKey(CompetitionDataset,null=True,blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.phasenumber)

class CompetitionParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    competition = models.ForeignKey(Competition,related_name='participation')
    status = models.ForeignKey(ParticipantStatus)
    reason = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        unique_together = (('user','competition'),)

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


