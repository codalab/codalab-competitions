from django.db import models
from django.conf import settings
from publish.models import Publishable
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.text import slugify
from django.utils.timezone import utc,now

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
        unique_together = (('object_id','content_type','entity'),)
    
class Page(Publishable):
    pagecontainer = models.ForeignKey(PageContainer,related_name='pages')
    rank = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=100, null=True, blank=True)
    visible = models.BooleanField(default=True)
    markup = models.TextField(blank=True)
    html = models.TextField(blank=True)

    class Meta(Publishable.Meta): 
        ordering = ["rank"]

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

class Competition(Publishable):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='logos',null=True,blank=True)
    has_registration = models.BooleanField(default=False)
    end_date = models.DateField(null=True,blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_creator')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_modified_by')
    last_modified = models.DateTimeField(auto_now_add=True)
    pagecontainer = generic.GenericRelation(PageContainer)

    class Meta(Publishable.Meta):
        permissions = (
            ('is_owner', 'Owner'),
            ('can_edit', 'Edit'),
            )
        ordering = ['end_date']

    def __unicode__(self):
        return self.title
    
    @property
    def is_active(self):
        return self.end_date < now().date()

class CompetitionDataset(Publishable):
    competition = models.ForeignKey(Competition)
    number = models.PositiveIntegerField(default=0)
    datafile = models.ForeignKey(ExternalFile)

    class Meta(Publishable.Meta):
        ordering = ["number"]

class CompetitionPhase(Publishable):
    competition = models.ForeignKey(Competition,related_name='phases')
    phasenumber = models.PositiveIntegerField()
    label = models.CharField(max_length=50,blank=True)
    start_date = models.DateTimeField()
    max_submissions = models.PositiveIntegerField(default=100)
    datasets = models.ManyToManyField(CompetitionDataset,blank=True,related_name='phase')


    class Meta(Publishable.Meta):
        ordering = ['phasenumber']

    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.phasenumber)

    @property
    def is_active(self):
        next_phase = self.competition.phases.filter(phasenumber=self.phasenumber+1)
        return self.start_date <= now().date() and (next_phase and next_phase[0].start_date > now().date())

class CompetitionParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='participation')
    competition = models.ForeignKey(Competition,related_name='participants')
    status = models.ForeignKey(ParticipantStatus)
    reason = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        unique_together = (('user','competition'),)

    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.user.username)


class CompetitionEntryStatus(models.Model):
    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20)
    
    def __unicode__(self):
        return self.name

class CompetitionEntry(models.Model):
    participant = models.ForeignKey(CompetitionParticipant)
    phase = models.ForeignKey(CompetitionPhase)
    submitted_at = models.DateTimeField()
    status = models.ForeignKey(CompetitionEntryStatus)
    status_details = models.CharField(max_length=100)
    
    
    def save(self,*args,**kwargs):
        if self.participant.competition != self.phase.competition:
            raise IntegrityError("Competition for phase and participant must be the same")
        return super(CompetitionSubmission,self).save(*args,**kwargs)

class ScoreLabel(models.Model):
    label = models.CharField(max_length=20)

    def __unicode__(self):
        return label

class CompetitionEntryScore(models.Model):
    entry = models.ForeignKey(CompetitionEntry)
    score_label = models.ForeignKey(ScoreLabel)
    score = models.DecimalField(default='0.0',decimal_places=12,max_digits=30,null=True,blank=True)
    
