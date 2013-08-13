import os
from django.db import models
from django.db.models import Max
from django.dispatch import receiver
import django.dispatch
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.text import slugify
from django.utils.timezone import utc,now

from mptt.models import MPTTModel, TreeForeignKey
from guardian.shortcuts import assign_perm

from os.path import abspath, basename, dirname, join, normpath

import signals
import tasks

# Competition Content
class ContentVisibility(models.Model):
    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20,unique=True)
    classname = models.CharField(max_length=30,null=True,blank=True)

    def __unicode__(self):
        return self.name

class ContentCategory(MPTTModel):
    parent = TreeForeignKey('self', related_name='children', null=True, blank=True)
    name = models.CharField(max_length=100)
    codename = models.SlugField(max_length=100,unique=True)
    visibility = models.ForeignKey(ContentVisibility)
    is_menu = models.BooleanField(default=True)
    content_limit = models.PositiveIntegerField(default=1)

    def __unicode__(self):
        return self.name

class DefaultContentItem(models.Model):
    category = TreeForeignKey(ContentCategory)
    label = models.CharField(max_length=100)
    codename = models.SlugField(max_length=100,unique=True)
    rank = models.IntegerField(default=0)
    required = models.BooleanField(default=False)
    initial_visibility =  models.ForeignKey(ContentVisibility)

    def __unicode__(self):
        return self.label

class PageContainer(models.Model):
    name = models.CharField(max_length=200,blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    owner = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = (('object_id','content_type'),)

    def __unicode__(self):
        return self.name

    def save(self,*args,**kwargs):      
        self.name = "%s - %s" % (self.owner.__unicode__(), self.name if self.name else str(self.pk))
        return super(PageContainer,self).save(*args,**kwargs)
  
class Page(models.Model):
    category = TreeForeignKey(ContentCategory)
    defaults = models.ForeignKey(DefaultContentItem, null=True, blank=True)
    codename = models.SlugField(max_length=100,unique=True)
    container = models.ForeignKey(PageContainer, related_name='pages')
    title = models.CharField(max_length=100, null=True, blank=True)
    label = models.CharField(max_length=100)
    rank = models.IntegerField(default=0)
    visibility = models.BooleanField(default=True)
    markup = models.TextField(blank=True)
    html = models.TextField(blank=True)

    class Meta: 
        ordering = ["rank"]
        
    def __unicode__(self):
        return self.title
    
    class Meta:
        unique_together = (('label','category'),)
        ordering = ['rank']

    def save(self,*args,**kwargs):
        if not self.title:
            self.title = "%s - %s" % ( self.container.name,self.label) 
        if self.defaults:
            if self.category != self.defaults.category:
                raise Exception("Defaults category must match Item category")
            if self.defaults.required and self.visibility is False:
                raise Exception("Item is required and must be visible")
        return super(Page,self).save(*args,**kwargs)

# External Files (These might be able to be removed, per a discussion 2013.7.29)    

class ExternalFileType(models.Model):
    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20,unique=True)

    def __unicode__(self):
        return self.name

class ExternalFileSource(models.Model):
    name = models.CharField(max_length=50)
    codename = models.SlugField(max_length=50,unique=True)
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
# End External File Models

# Join+ Model for Participants of a competition
class ParticipantStatus(models.Model):
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30,unique=True)
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Competition(models.Model):
    """ This is the base competition. """
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='logos',null=True,blank=True)
    image_url_base = models.CharField(max_length=255)
    has_registration = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True,blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_creator')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_modified_by')
    last_modified = models.DateTimeField(auto_now_add=True)
    pagecontent = models.ForeignKey(PageContainer,null=True,blank=True)

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
    
    def save(self,*args,**kwargs):
        # Make sure the image_url_base is set from the actual storage implementation
        self.image_url_base = self.image.storage.url('')
        # Do the real save
        return super(Competition,self).save(*args,**kwargs)
        
    def image_url(self):
        # Return the transformed image_url
        if self.image:
            return os.path.join(self.image_url_base,self.image.name)
        return None
        
    @property
    def is_active(self):
        return self.end_date < now().date()

# Dataset model
class Dataset(models.Model):
    """ 
        This is a dataset for a competition. 
        TODO: Consider if this is replaced or reimplemented as a 'bundle of data'. 
    """
    creator =  models.ForeignKey(settings.AUTH_USER_MODEL, related_name='datasets')
    name = models.CharField(max_length=50)
    description = models.TextField()
    number = models.PositiveIntegerField(default=1)
    datafile = models.ForeignKey(ExternalFile)

    class Meta:
        ordering = ["number"]

    def __unicode__(self):
        return "%s [%s]" % (self.name,self.datafile.name)

# Competition Phase 
class CompetitionPhase(models.Model):
    """ 
        A phase of a competition.
    """
    competition = models.ForeignKey(Competition,related_name='phases')
    phasenumber = models.PositiveIntegerField()
    label = models.CharField(max_length=50, blank=True)
    start_date = models.DateTimeField()
    max_submissions = models.PositiveIntegerField(default=100)
    datasets = models.ManyToManyField(Dataset, blank=True, related_name='phase')

    class Meta:
        ordering = ['phasenumber']

    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.phasenumber)

    @property
    def is_active(self):
        next_phase = self.competition.phases.filter(phasenumber=self.phasenumber+1)
        return self.start_date <= now() and (next_phase and next_phase[0].start_date > now())


# Competition Participant
class CompetitionParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='participation')
    competition = models.ForeignKey(Competition,related_name='participants')
    status = models.ForeignKey(ParticipantStatus)
    reason = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        unique_together = (('user','competition'),)

    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.user.username)

# Competition Submission Status 
class CompetitionSubmissionStatus(models.Model):
    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20,unique=True)
    
    def __unicode__(self):
        return self.name



def submission_file_name(instance,filename):
    
    return "competition/%d/%d/submissions/%d/%s/predictions.zip" % (instance.phase.competition.pk,
                                                                    instance.phase.pk,
                                                                    instance.participant.user.pk,
                                                                    instance.submission_number)
        
# Competition Submission
class CompetitionSubmission(models.Model):
    participant = models.ForeignKey(CompetitionParticipant)
    phase = models.ForeignKey(CompetitionPhase)
    file = models.FileField(upload_to=submission_file_name, null=True,blank=True)
    file_url_base = models.CharField(max_length=2000,blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(CompetitionSubmissionStatus)
    status_details = models.CharField(max_length=100,null=True,blank=True)   
    submission_number = models.PositiveIntegerField(default=0)
    
    _fileobj = None
    _do_submission = False

    class Meta:
        unique_together = (('submission_number','phase','participant'),)

    def __unicode__(self):
        return "%s %s %s %s" % (self.pk, self.phase.competition.title, self.phase.label,self.participant.user.email)


    def save(self,*args,**kwargs):
        # only at save on object creation should it be submitted
        subnum = CompetitionSubmission.objects.select_for_update().filter(phase=self.phase).aggregate(Max('submission_number'))['submission_number__max']
        if subnum is not None:
            self.submission_number = subnum + 1
        else:
            self.submission_number = 1
        if not self.pk:
            self._do_submission = True
            self.set_status('submitted',force_save=False)
        else:
            self._do_submission = False
        if self.participant.competition != self.phase.competition:
            raise Exception("Competition for phase and participant must be the same")
        self.file_url_base = self.file.storage.url('')
        res = super(CompetitionSubmission,self).save(*args,**kwargs)
        if self._do_submission:
            signals.do_submission.send(sender=CompetitionSubmission, instance=self)
        return res
    
    def file_url(self):
        if self.file:
            return os.path.join(self.file_url_base, self.file.name)
        return None

    def set_status(self,status,force_save=False):
        self.status = CompetitionSubmissionStatus.objects.get(codename=status)
        if force_save:
            self.save()

@receiver(signals.do_submission)
def do_submission_task(sender,instance=None,**kwargs):
    tasks.submission_run.delay(instance.file_url(), submission_id=instance.pk)

# Competition Submission Results
class SubmissionResult(models.Model):
    submission = models.OneToOneField(CompetitionSubmission,related_name='result')
    aggregate = models.DecimalField(max_digits=22,decimal_places=10)

class SubmissionScore(models.Model):
    result = models.ForeignKey(SubmissionResult,related_name='scores')
    label = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=20,decimal_places=10)

    class Meta:
        ordering = ['label']

class PhaseLeaderBoard(models.Model):
    phase = models.OneToOneField(CompetitionPhase,related_name='board')
    is_open = models.BooleanField(default=True)
    
    def submissions(self):
        return CompetitionSubmission.objects.filter(leaderboard_entry__board=self)
    
    def __unicode__(self):
        return "%s [%s]" % (self.phase.label,'Open' if self.is_open else 'Closed')  

    def is_open(self):
        """
        The default implementation passes through the leaderboard is_open check to the phase is_active check.
        """
        self.is_open = self.phase.is_active
        return self.phase.is_active
       
class PhaseLeaderBoardEntry(models.Model):
    board = models.ForeignKey(PhaseLeaderBoard,related_name='entries')
    submission = models.ForeignKey(CompetitionSubmission,related_name='leaderboard_entry')
            
    class Meta:
        unique_together = (('board','submission'),)


# Bundle Model
class Bundle(models.Model):
    path = models.CharField(max_length=100, blank=True)
    inputpath = models.CharField(max_length=100, blank=True)
    outputpath = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    #owner = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=100)
    metadata = models.CharField(max_length=500)
    private = models.BooleanField()
  
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
  
    def get_absolute_url(self):
        return ('project_bundle_detail', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)




# Run Model
class Run(models.Model):
    bundle = models.ForeignKey(Bundle)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, max_length=255)
    metadata = models.CharField(max_length=255)
    bundlePath = dirname(dirname(abspath(__file__)))
    programPath = models.CharField(max_length=100)
    inputPath = models.CharField(max_length=100)
    outputPath = models.CharField(max_length=100)
    cellout = models.FloatField(blank=True, null=True)
  
    objects = models.Manager() 
  
    class Meta:
        ordering = ['-created']
    
    def __unicode__(self):
        return u'%s' % self.bundle
  
    def get_absolute_url(self):
        return ('bundle_run_detail', (), {'object_id': self.id })
    get_absolute_url = models.permalink(get_absolute_url)
