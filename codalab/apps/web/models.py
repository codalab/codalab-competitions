from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.text import slugify
from django.utils.timezone import utc,now

from mptt.models import MPTTModel, TreeForeignKey
from guardian.shortcuts import assign_perm

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

class ContentEntity(MPTTModel):
    parent = TreeForeignKey('self', related_name='children', null=True, blank=True)
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
        return "%s - %s" % (self.container.name, self.label)

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
    entity = TreeForeignKey(ContentEntity)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    owner = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('object_id','content_type','entity'),)
        
    def __unicode__(self):
        return "%s [%s]" % (self.owner.__unicode__(), self.entity.__unicode__())


class Page(models.Model):
    pagecontainer = models.ForeignKey(PageContainer,related_name='pages')
    rank = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=100, null=True, blank=True)
    visible = models.BooleanField(default=True)
    markup = models.TextField(blank=True)
    html = models.TextField(blank=True)

    class Meta: 
        ordering = ["rank"]

    def __unicode__(self):
        return self.title

class ExternalFileType(models.Model):
    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20)

    def __unicode__(self):
        return self.name

class ExternalFileSource(models.Model):
    name = models.CharField(max_length=50)
    codename = models.SlugField(max_length=50)
    service_url = models.URLField(null=True,blank=True)

    def __unicode__(self):
        return self.name

class ExternalFile(models.Model):
    type = models.ForeignKey(ExternalFileType)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=100)
    source_url = models.URLField()
    source_address_info = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name

class ParticipantStatus(models.Model):
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30)
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Competition(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='logos',null=True,blank=True)
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
        ordering = ['end_date']

    def __unicode__(self):
        return self.title
    
    def set_owner(self,user):
        return assign_perm('view_task', user, self)
        
    @property
    def is_active(self):
        return self.end_date < now().date()

class Dataset(models.Model):
    creator =  models.ForeignKey(settings.AUTH_USER_MODEL, related_name='datasets')
    name = models.CharField(max_length=50)
    description = models.TextField()
    number = models.PositiveIntegerField(default=1)
    datafile = models.ForeignKey(ExternalFile)

    class Meta:
        ordering = ["number"]

    def __unicode__(self):
        return "%s [%s]" % (self.name,self.datafile.name)

class CompetitionPhase(models.Model):
    competition = models.ForeignKey(Competition,related_name='phases')
    phasenumber = models.PositiveIntegerField()
    label = models.CharField(max_length=50, blank=True)
    start_date = models.DateTimeField()
    max_submissions = models.PositiveIntegerField(default=100)
    datasets = models.ManyToManyField(Dataset, blank=True,related_name='phase')

    class Meta:
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


class CompetitionSubmissionStatus(models.Model):
    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20)
    
    def __unicode__(self):
        return self.name

class CompetitionSubmission(models.Model):
    participant = models.ForeignKey(CompetitionParticipant)
    phase = models.ForeignKey(CompetitionPhase)
    file = models.ForeignKey(ExternalFile)
    submitted_at = models.DateTimeField()
    status = models.ForeignKey(CompetitionSubmissionStatus)
    status_details = models.CharField(max_length=100)   
    
<<<<<<< HEAD

# Bundle Model
class Bundle(models.Model):
  title = models.CharField(max_length=100,null=True,blank=True)
  created = models.DateTimeField(auto_now_add=True)
  #submitter = models.ForeignKey(User)
  #published = models.BooleanField(default=True)
  url = models.URLField("URL", max_length=250, blank=True)
  description = models.TextField(blank=True)
    
  def __unicode__(self):
    return self.title

class Run(models.Model):
    bundle = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    metadata = models.CharField(max_length=255)
    program = models.CharField(max_length=255)
    #published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return u'%s' % self.bundle

    def get_absolute_url(self):
        return reverse('bundle.views.run', args=[self.slug])
=======
    def save(self,*args,**kwargs):
        if self.participant.competition != self.phase.competition:
            raise IntegrityError("Competition for phase and participant must be the same")
        if self.participant.user != self.file.creator:
            raise IntegrityError("Participant can only submit their own files")
        return super(CompetitionSubmission,self).save(*args,**kwargs)

class CompetitionSubmissionResults(models.Model):
    submission = models.ForeignKey(CompetitionSubmission)
    payload = models.TextField()
>>>>>>> master
