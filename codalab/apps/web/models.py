import exceptions
import os
import operator
import requests
from django.db import models
from django.db import IntegrityError
from django.db.models import Max
from django.dispatch import receiver
import django.dispatch
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.text import slugify
from django.utils.timezone import utc,now
from django.core.exceptions import PermissionDenied
from django.core.files.storage import get_storage_class
from mptt.models import MPTTModel, TreeForeignKey
from guardian.shortcuts import assign_perm

from os.path import abspath, basename, dirname, join, normpath

import signals
import tasks

## Needed for computation service handling
## Hack for now
StorageClass = get_storage_class(settings.DEFAULT_FILE_STORAGE)
try:
    PrivateStorage = StorageClass(account_name=settings.PRIVATE_AZURE_ACCOUNT_NAME,
                                         account_key=settings.PRIVATE_AZURE_ACCOUNT_KEY,
                                         azure_container=settings.PRIVATE_AZURE_CONTAINER)

    BundleStorage = StorageClass(account_name=settings.BUNDLE_AZURE_ACCOUNT_NAME,
                                        account_key=settings.BUNDLE_AZURE_ACCOUNT_KEY,
                                        azure_container=settings.BUNDLE_AZURE_CONTAINER)

    PublicStorage = StorageClass(account_name=settings.AZURE_ACCOUNT_NAME,
                                        account_key=settings.AZURE_ACCOUNT_KEY,
                                        azure_container=settings.AZURE_CONTAINER)

except:
    PrivateStorage = StorageClass()
    BundleStorage = StorageClass()
    PublicStorage = StorageClass()

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
    codename = models.SlugField(max_length=100)
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
        unique_together = (('label','category','container'),)
        ordering = ['rank']

    def save(self,*args,**kwargs):
        if not self.title:
            self.title = "%s - %s" % ( self.container.name,self.label ) 
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
    UNKNOWN = 'unknown'
    DENIED = 'denied'
    APPROVED = 'approved'
    PENDING = 'pending'
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30,unique=True)
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Competition(models.Model):
    """ This is the base competition. """
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='logos', storage=PublicStorage, null=True, blank=True)
    image_url_base = models.CharField(max_length=255)
    has_registration = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True,blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_creator')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_modified_by')
    last_modified = models.DateTimeField(auto_now_add=True)
    pagecontainers = generic.GenericRelation(PageContainer)

    @property
    def pagecontent(self):
        items = list(self.pagecontainers.all())
        return items[0] if len(items) > 0 else None

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
        return True if self.end_date is None else self.end_date < now().date()

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


def phase_data_prefix(phase):
    return "competition/%d/%d/data/" % (phase.competition.pk, phase.pk,)

# In the following helpers, the filename argument is required even though we
# choose to not use it. See FileField.upload_to at https://docs.djangoproject.com/en/dev/ref/models/fields/.

def phase_scoring_program_file(phase, filename=""):
    return phase_data_prefix(phase) + 'program.zip'

def phase_reference_data_file(phase, filename=""):
    return phase_data_prefix(phase) + 'reference.zip'

def phase_input_data_file(phase, filename=""):
    return phase_data_prefix(phase) + 'input.zip'

def submission_file_name(instance,filename):
    return "competition/%d/%d/submissions/%d/%s/predictions.zip" % (instance.phase.competition.pk,
                                                                    instance.phase.pk,
                                                                    instance.participant.user.pk,
                                                                    instance.submission_number)
def submission_inputfile_name(instance, filename):
     return "competition/%d/%d/submissions/%d/%s/input.txt" % (instance.phase.competition.pk,
                                                               instance.phase.pk,
                                                               instance.participant.user.pk,
                                                               instance.submission_number)
def submission_runfile_name(instance, filename):
    return "competition/%d/%d/submissions/%d/%s/run.txt" % (instance.phase.competition.pk,
                                                            instance.phase.pk,
                                                            instance.participant.user.pk,
                                                            instance.submission_number)

def submission_output_filename(instance,filename=""):
    return "competition/%d/%d/submissions/%d/%s/run/output.zip" % (instance.phase.competition.pk,
                                                                   instance.phase.pk,
                                                                   instance.participant.user.pk,
                                                                   instance.submission_number)
def submission_stdout_filename(instance,filename=""):
    return "competition/%d/%d/submissions/%d/%s/run/stdout.txt" % (instance.phase.competition.pk,
                                                                   instance.phase.pk,
                                                                   instance.participant.user.pk,
                                                                   instance.submission_number)
def submission_stderr_filename(instance,filename=""):
    return "competition/%d/%d/submissions/%d/%s/run/stderr.txt" % (instance.phase.competition.pk,
                                                                   instance.phase.pk,
                                                                   instance.participant.user.pk,
                                                                   instance.submission_number)
def submission_file_blobkey(instance, filename="run/output.zip"):
    return "competition/%d/%d/submissions/%d/%s/%s" % (instance.phase.competition.pk,
                                                       instance.phase.pk,
                                                       instance.participant.user.pk,
                                                       instance.submission_number,
                                                       filename)

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
    is_scoring_only = models.BooleanField(default=True)
    scoring_program = models.FileField(upload_to=phase_scoring_program_file, storage=BundleStorage,null=True,blank=True)
    reference_data = models.FileField(upload_to=phase_reference_data_file, storage=BundleStorage,null=True,blank=True)
    input_data = models.FileField(upload_to=phase_input_data_file, storage=BundleStorage,null=True,blank=True)
    datasets = models.ManyToManyField(Dataset, blank=True, related_name='phase')
    
    class Meta:
        ordering = ['phasenumber']

    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.phasenumber)

    @property
    def is_active(self):
        """ Returns true when this phase of the competition is on-going. """
        next_phase = self.competition.phases.filter(phasenumber=self.phasenumber+1)
        if (next_phase and len(next_phase) > 0):
            # there a phase following this phase: this phase ends when the next phase starts
            return self.start_date <= now() and (next_phase and next_phase[0].start_date > now())
        else:
            # there is no phase following this phase: this phase ends when the competition ends
            return self.competition.is_active

    @property
    def is_future(self):
        """ Returns true if this phase of the competition has yet to start. """
        return now() < self.start_date

    @property
    def is_past(self):
        """ Returns true if this phase of the competition has already ended. """
        return (not is_active) and (not is_future)

    @staticmethod
    def rank_values(ids, id_value_pairs, sort_ascending=True, eps=1.0e-12):
        """ Given a set of identifiers (ids) and a set of (id, value)-pairs
            computes a ranking based on the value. The ranking is provided 
            as a set of (id, rank) pairs for all id in ids.
        """
        ranks = {}
        # Only keep pairs for which the key is in the list of ids
        valid_pairs = {k: v for k, v in id_value_pairs.iteritems() if k in ids}
        if len(valid_pairs) == 0:
            return {id: 1 for id in ids}
        # Sort and compute ranks
        sorted_pairs = sorted(valid_pairs.iteritems(), key = operator.itemgetter(1), reverse=not sort_ascending)
        r = 1
        k, v = sorted_pairs[0]
        ranks[k] = r
        for i in range(1, len(sorted_pairs)):
            k, vnow = sorted_pairs[i]
            # Increment the rank only when values are different
            if abs(vnow - v) > eps:
                r = r + 1
                v = vnow
            ranks[k] = r
        # Fill in ranks for ids which were not seen in the input
        r = r + 1
        for id in ids:
            if id not in ranks:
                ranks[id] = r
        return ranks

    @staticmethod 
    def format_value(v, precision="2"):
        p = 1
        try:
            if precision is not None:
                p = min(10, max(1, int(precision)))
        except exceptions.ValueError:
            pass
        return ("{:." + str(p) + "f}").format(v)


    def scores(self,**kwargs):

        score_filters = kwargs.pop('score_filters',{})

        # Get the list of submissions in this leaderboard
        submissions = []
        lb, created = PhaseLeaderBoard.objects.get_or_create(phase=self)
        if not created:
            for e in PhaseLeaderBoardEntry.objects.filter(board=lb):
                submissions.append((e.result.pk, e.result.participant.user.username))

        results = []
        for g in SubmissionResultGroup.objects.filter(phases__in=[self]).order_by('ordering'):
            label = g.label
            headers = []
            scores = {}
            for (pk,name) in submissions: scores[pk] = {'username': name, 'values': []}

            scoreDefs = []
            currentColumnLabels = {}
            for x in SubmissionScoreSet.objects.order_by('tree_id','lft').filter(scoredef__isnull=False,
                                                                        scoredef__groups__in=[g],
                                                                        **kwargs):
                if x.parent is not None:
                    columnLabel = x.parent.label
                    columnSubLabels = [x.label]
                else:
                    columnLabel = x.label
                    columnSubLabels = []
                if columnLabel not in currentColumnLabels:
                    currentColumnLabels[columnLabel] = len(headers)
                    headers.append({columnLabel : columnSubLabels})
                else:
                    headers[currentColumnLabels[columnLabel]][columnLabel].extend(columnSubLabels)

                scoreDefs.append(x.scoredef)
                            
            column_span = 2
            for gHeader in headers:
                for k in gHeader:
                    n = len(gHeader[k])
                    column_span += n if n > 0 else 1

            results.append({ 'label': label, 'headers': headers, 'total_span' : column_span, 'scores': scores, 'scoredefs': scoreDefs })


        if len(submissions) > 0:
            # Figure out which submission scores we need to read from the database.
            submission_ids = [id for (id,name) in submissions]
            not_computed_scoredefs = {}
            computed_scoredef_ids = []
            computed_deps = {}
            for result in results:
                for sdef in result['scoredefs']:
                    if sdef.computed is True:
                        computed_scoredef_ids.append(sdef.id)
                    else:
                        not_computed_scoredefs[sdef.key] = sdef
                if len(computed_scoredef_ids) > 0:
                    computed_ids = SubmissionComputedScore.objects.filter(scoredef_id__in=computed_scoredef_ids).values_list('id')
                    fields = SubmissionComputedScoreField.objects.filter(computed_id__in=computed_ids)
                    for field in fields:
                        if not field.scoredef.computed:
                            not_computed_scoredefs[field.scoredef.key] = field.scoredef
                        if field.computed.scoredef.key not in computed_deps:
                            computed_deps[field.computed.scoredef.key] = []
                        computed_deps[field.computed.scoredef.key].append(field.scoredef)
            # Now read the submission scores
            values = {}
            scoredef_ids = [sdef.id for (sdef_key, sdef) in not_computed_scoredefs.iteritems()]
            for s in SubmissionScore.objects.filter(scoredef_id__in=scoredef_ids, result_id__in=submission_ids):
                if s.scoredef.key not in values:
                    values[s.scoredef.key] = {}
                values[s.scoredef.key][s.result.pk] = s.value

            # rank values per scoredef.key (not computed)
            ranks = {}
            for (sdef_key, v) in values.iteritems():
                sdef = not_computed_scoredefs[sdef_key]
                ranks[sdef_key] = self.rank_values(submission_ids, v, sort_ascending=sdef.sorting=='asc')

            # compute values for computed scoredefs
            for result in results:
                for sdef in result['scoredefs']:
                    if sdef.computed:
                        operation = getattr(models, sdef.computed_score.operation)
                        if (operation.name == 'Avg'):
                            cnt = len(computed_deps[sdef.key])
                            if (cnt > 0):
                                computed_values = {}
                                for id in submission_ids:
                                    computed_values[id] = sum([ranks[d.key][id] for d in computed_deps[sdef.key]]) / float(cnt)                                    
                                values[sdef.key] = computed_values

            #format values
            for result in results:
                scores = result['scores']
                for sdef in result['scoredefs']:
                    knownValues = {}
                    if sdef.key in values:
                        knownValues = values[sdef.key]
                    knownRanks = {}
                    if sdef.key in ranks:
                        knownRanks = ranks[sdef.key]
                    for id in submission_ids:
                        v = "-"
                        if id in knownValues:
                            v = CompetitionPhase.format_value(knownValues[id], sdef.numeric_format)
                        r = "-"
                        if id in knownRanks:
                            r = knownRanks[id]
                        if sdef.show_rank:
                            scores[id]['values'].append({'val': v, 'rnk': r})
                        else:
                            scores[id]['values'].append({'val': v, 'hidden_rnk': r})

        for result in results:
            del result['scoredefs']        

        return results

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

    @property
    def is_approved(self):
        """ Returns true if this participant is approved into the competition. """
        return self.status.codename == ParticipantStatus.APPROVED

# Competition Submission Status 
class CompetitionSubmissionStatus(models.Model):
    SUBMITTING = "submitting"
    SUBMITTED = "submitted"
    RUNNING = "running"
    FAILED = "failed"
    CANCELLED = "cancelled"
    FINISHED = "finished"

    name = models.CharField(max_length=20)
    codename = models.SlugField(max_length=20,unique=True)
    
    def __unicode__(self):
        return self.name

# Competition Submission
class CompetitionSubmission(models.Model):
    participant = models.ForeignKey(CompetitionParticipant, related_name='submissions')
    phase = models.ForeignKey(CompetitionPhase, related_name='submissions')
    file = models.FileField(upload_to=submission_file_name, storage=BundleStorage, null=True, blank=True)
    file_url_base = models.CharField(max_length=2000,blank=True)
    inputfile = models.FileField(upload_to=submission_inputfile_name, storage=BundleStorage, null=True, blank=True)
    runfile = models.FileField(upload_to=submission_runfile_name, storage=BundleStorage, null=True,blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    execution_key = models.TextField(blank=True,default="")
    status = models.ForeignKey(CompetitionSubmissionStatus)
    status_details = models.CharField(max_length=100,null=True,blank=True)   
    submission_number = models.PositiveIntegerField(default=0)
    output_file = models.FileField(upload_to=submission_output_filename, storage=BundleStorage, null=True, blank=True)
    stdout_file = models.FileField(upload_to=submission_stdout_filename, storage=BundleStorage, null=True, blank=True)
    stderr_file = models.FileField(upload_to=submission_stderr_filename, storage=BundleStorage, null=True, blank=True)

    _fileobj = None
    _do_submission = False

    class Meta:
        unique_together = (('submission_number','phase','participant'),)

    def __unicode__(self):
        return "%s %s %s %s" % (self.pk, self.phase.competition.title, self.phase.label, self.participant.user.email)

    def save(self,*args,**kwargs):
        if self.participant.competition != self.phase.competition:
            raise Exception("Competition for phase and participant must be the same")
        # only at save on object creation should it be submitted
        if not self.pk:
            subnum = CompetitionSubmission.objects.select_for_update().filter(phase=self.phase, participant=self.participant).aggregate(Max('submission_number'))['submission_number__max']
            if subnum is not None:
                self.submission_number = subnum + 1
            else:
                self.submission_number = 1
            if (self.submission_number > self.phase.max_submissions):
                raise PermissionDenied("The maximum number of submissions has been reached.")
            self._do_submission = True
            self.set_status(CompetitionSubmissionStatus.SUBMITTING,force_save=False)
        else:
            self._do_submission = False
        self.file_url_base = self.file.storage.url('')
        res = super(CompetitionSubmission,self).save(*args,**kwargs)
        if self._do_submission:
            signals.do_submission.send(sender=CompetitionSubmission, instance=self)
        return res
    
    def file_url(self):
        if self.file:
            return os.path.join(self.file_url_base, self.file.name)
        return None

    def runfile_url(self):
        if self.runfile:
            return os.path.join(self.runfile.storage.url(''), self.runfile.name)
        return None

    def inputfile_url(self):
        if self.inputfile:
            return os.path.join(self.inputfile.storage.url(''), self.inputfile.name)
        return None

    def get_execution_status(self):
        if self.execution_key:
            res = requests.get(settings.COMPUTATION_SUBMISSION_URL + self.execution_key)
            if res.status_code in (200,):
                return res.json()
        return None

    def set_status(self,status,force_save=False):
        self.status = CompetitionSubmissionStatus.objects.get(codename=status)
        if force_save:
            self.save()


@receiver(signals.do_submission)
def do_submission_task(sender,instance=None,**kwargs):
    tasks.submission_run.delay(instance.file_url(), submission_id=instance.pk)

class SubmissionResultGroup(models.Model):   
    competition = models.ForeignKey(Competition)
    key = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    ordering = models.PositiveIntegerField(default=1)
    phases = models.ManyToManyField(CompetitionPhase,through='SubmissionResultGroupPhase')

    class Meta:
        ordering = ['ordering']

class SubmissionResultGroupPhase(models.Model):
    group = models.ForeignKey(SubmissionResultGroup)
    phase = models.ForeignKey(CompetitionPhase)
    
    class Meta:
        unique_together = (('group','phase'),)

    def save(self,*args,**kwargs):
        if self.group.competition != self.phase.competition:
            raise IntegrityError("Group and Phase competition must be the same")
        super(SubmissionResultGroupPhase,self).save(*args,**kwargs)

class SubmissionScoreDef(models.Model):
    competition = models.ForeignKey(Competition)
    key = models.SlugField(max_length=50)
    label = models.CharField(max_length=50)
    sorting = models.SlugField(max_length=20,default='asc',choices=(('asc','Ascending'),('desc','Descending')))
    numeric_format = models.CharField(max_length=20,blank=True,null=True)
    show_rank = models.BooleanField(default=False)
    selection_default = models.IntegerField(default=0)
    computed = models.BooleanField(default=False)
    groups = models.ManyToManyField(SubmissionResultGroup,through='SubmissionScoreDefGroup')

    class Meta:
        unique_together = (('key','competition'),)

    def __unicode__(self):
        return self.label

class SubmissionScoreDefGroup(models.Model):
    scoredef = models.ForeignKey(SubmissionScoreDef)
    group = models.ForeignKey(SubmissionResultGroup)

    class Meta:
        unique_together = (('scoredef','group'),)
    
    def __unicode__(self):
        return "%s %s" % (self.scoredef,self.group)

    def save(self,*args,**kwargs):
        if self.scoredef.competition != self.group.competition:
            raise IntegrityError("Score Def competition and phase compeition must be the same")
        super(SubmissionScoreDefGroup,self).save(*args,**kwargs)

class SubmissionComputedScore(models.Model):
    scoredef = models.OneToOneField(SubmissionScoreDef, related_name='computed_score')
    operation = models.CharField(max_length=10,choices=(('Max','Max'),
                                                        ('Avg', 'Average')))
    
class SubmissionComputedScoreField(models.Model):
    computed = models.ForeignKey(SubmissionComputedScore,related_name='fields')
    scoredef = models.ForeignKey(SubmissionScoreDef)

    def save(self,*args,**kwargs):
        if self.scoredef.computed is True:
            raise IntegrityError("Cannot use a computed field for a computed score")
        super(SubmissionComputedScoreField,self).save(*args,**kwargs)
        
class SubmissionScoreSet(MPTTModel):
    parent = TreeForeignKey('self',null=True,blank=True, related_name='children')
    competition = models.ForeignKey(Competition)
    key = models.CharField(max_length=50,unique=True)
    label = models.CharField(max_length=50)
    scoredef = models.ForeignKey(SubmissionScoreDef,null=True,blank=True)

    def __unicode__(self):
        return "%s %s" % (self.parent.label if self.parent else None, self.label)

        
class SubmissionScore(models.Model):
    result = models.ForeignKey(CompetitionSubmission, related_name='scores')
    scoredef = models.ForeignKey(SubmissionScoreDef)
    value = models.DecimalField(max_digits=20, decimal_places=10)

    class Meta:
        unique_together = (('result','scoredef'),)
    
    def save(self,*args,**kwargs):
        if self.scoredef.computed is True and value:
            raise IntegrityError("Score is computed. Cannot assign a value")
        super(SubmissionScore,self).save(*args,**kwargs)

class PhaseLeaderBoard(models.Model):
    phase = models.OneToOneField(CompetitionPhase,related_name='board')
    is_open = models.BooleanField(default=True)
    
    def submissions(self):
        return CompetitionSubmission.objects.filter(leaderboard_entry_result__board=self)
    
    def __unicode__(self):
        return "%s [%s]" % (self.phase.label,'Open' if self.is_open else 'Closed')  

    def is_open(self):
        """
        The default implementation passes through the leaderboard is_open check to the phase is_active check.
        """
        self.is_open = self.phase.is_active
        return self.phase.is_active
       
    def scores(self,**kwargs):
        return self.phase.scores(score_filters=dict(result__leaderboard_entry_result__board=self))
    
class PhaseLeaderBoardEntry(models.Model):
    board = models.ForeignKey(PhaseLeaderBoard, related_name='entries')
    result = models.ForeignKey(CompetitionSubmission,  related_name='leaderboard_entry_result')

    class Meta:
        unique_together = (('board', 'result'),)


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
    #get_absolute_url = models.permalink(get_absolute_url)


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
  
    #objects = models.Manager() 
  
    class Meta:
        ordering = ['-created']
    
    def __unicode__(self):
        return u'%s' % self.bundle
  
    def get_absolute_url(self):
        return ('bundle_run_detail', (), {'object_id': self.id })
    #get_absolute_url = models.permalink(get_absolute_url)
