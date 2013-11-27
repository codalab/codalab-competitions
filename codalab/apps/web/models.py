import exceptions
import logging
import random
import operator
import os, io
from os.path import abspath, basename, dirname, join, normpath
import zipfile
import yaml
import tempfile
import datetime
import django.dispatch
import time
from django.db import models
from django.db import IntegrityError
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.files.storage import get_storage_class
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.text import slugify
from django.utils.timezone import utc, now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from mptt.models import MPTTModel, TreeForeignKey
from guardian.shortcuts import assign_perm

logger = logging.getLogger(__name__)

## Needed for computation service handling
## Hack for now
StorageClass = get_storage_class(settings.DEFAULT_FILE_STORAGE)
try:
    BundleStorage = StorageClass(account_name=settings.BUNDLE_AZURE_ACCOUNT_NAME,
                                        account_key=settings.BUNDLE_AZURE_ACCOUNT_KEY,
                                        azure_container=settings.BUNDLE_AZURE_CONTAINER)

    PublicStorage = StorageClass(account_name=settings.AZURE_ACCOUNT_NAME,
                                        account_key=settings.AZURE_ACCOUNT_KEY,
                                        azure_container=settings.AZURE_CONTAINER)

except:
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
    published = models.BooleanField(default=False)

    @property
    def pagecontent(self):
        items = list(self.pagecontainers.all())
        return items[0] if len(items) > 0 else None

    def get_absolute_url(self):
        return reverse('competitions:view', kwargs={'pk':self.pk})

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
        if self.end_date is None:
            return True
        if type(self.end_date) is datetime.datetime.date:
            return True if self.end_date is None else self.end_date > now().date()
        if type(self.end_date) is datetime.datetime:
            return True if self.end_date is None else self.end_date > now()

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

def competition_prefix(competition):
    return os.path.join("competition", str(competition.id))

def phase_prefix(phase):
    return os.path.join(competition_prefix(phase.competition), str(phase.phasenumber))

def phase_data_prefix(phase):
    return os.path.join("competition", str(phase.competition.id), str(phase.phasenumber), "data")

# In the following helpers, the filename argument is required even though we
# choose to not use it. See FileField.upload_to at https://docs.djangoproject.com/en/dev/ref/models/fields/.

def phase_scoring_program_file(phase, filename="program.zip"):
    return os.path.join(phase_data_prefix(phase), filename)

def phase_reference_data_file(phase, filename="reference.zip"):
    return os.path.join(phase_data_prefix(phase), filename)

def phase_input_data_file(phase, filename="input.zip"):
    return os.path.join(phase_data_prefix(phase), filename)

def submission_root(instance):
    return os.path.join("competition", str(instance.phase.competition.pk), str(instance.phase.pk),
                        "submissions", str(instance.participant.user.pk), str(instance.submission_number))

def submission_file_name(instance, filename="predictions.zip"):
    return os.path.join(submission_root(instance), filename)

def submission_inputfile_name(instance, filename="input.txt"):
    return os.path.join(submission_root(instance), filename)

def submission_runfile_name(instance, filename="run.txt"):
    return os.path.join(submission_root(instance), filename)

def submission_output_filename(instance, filename="output.zip"):
    return os.path.join(submission_root(instance), "run", filename)

def submission_stdout_filename(instance, filename="stdout.txt"):
    return os.path.join(submission_root(instance), "run", filename)

def submission_stderr_filename(instance, filename="stderr.txt"):
    return os.path.join(submission_root(instance), "run", filename)

def submission_prediction_runfile_name(instance, filename="run.txt"):
    return os.path.join(submission_root(instance), "pred", filename)

def submission_prediction_output_filename(instance, filename="output.zip"):
    return os.path.join(submission_root(instance), "pred", "run", filename)

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
        if (next_phase is not None) and (len(next_phase) > 0):
            # there is a phase following this phase, thus this phase is active if the current date
            # is between the start of this phase and the start of the next phase
            return self.start_date <= now() and (now() < next_phase[0].start_date)
        else:
            # there is no phase following this phase, thus this phase is active if the current data
            # is after the start date of this phase and the competition is "active"
            return self.start_date <= now() and self.competition.is_active

    @property
    def is_future(self):
        """ Returns true if this phase of the competition has yet to start. """
        return now() < self.start_date

    @property
    def is_past(self):
        """ Returns true if this phase of the competition has already ended. """
        return (not self.is_active) and (not self.is_future)

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
    def rank_submissions(ranks_by_id):
        def compare_ranks(a, b):
            limit = 1000000
            try:
                ia = int(ranks_by_id[a])
            except exceptions.ValueError:
                ia = limit
            try:
                ib = int(ranks_by_id[b])
            except exceptions.ValueError:
                ib = limit
            return ia - ib
        return compare_ranks

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
            qs = PhaseLeaderBoardEntry.objects.filter(board=lb)
            for (rid, name) in qs.values_list('result_id', 'result__participant__user__username'):
                submissions.append((rid,  name))

        results = []
        for g in SubmissionResultGroup.objects.filter(phases__in=[self]).order_by('ordering'):
            label = g.label
            headers = []
            scores = {}
            for (pk,name) in submissions: scores[pk] = {'username': name, 'values': []}

            scoreDefs = []
            columnKeys = {} # maps a column key to its index in headers list
            for x in SubmissionScoreSet.objects.order_by('tree_id','lft').filter(scoredef__isnull=False,
                                                                        scoredef__groups__in=[g],
                                                                        **kwargs).select_related('scoredef', 'parent'):
                if x.parent is not None:
                    columnKey = x.parent.key
                    columnLabel = x.parent.label
                    columnSubLabels = [{'key': x.key, 'label': x.label}]
                else:
                    columnKey = x.key
                    columnLabel = x.label
                    columnSubLabels = []
                if columnKey not in columnKeys:
                    columnKeys[columnKey] = len(headers)
                    headers.append({'key' : columnKey, 'label': columnLabel, 'subs' : columnSubLabels})
                else:
                    headers[columnKeys[columnKey]]['subs'].extend(columnSubLabels)

                scoreDefs.append(x.scoredef)

            # compute total column span
            column_span = 2
            for gHeader in headers:
                n = len(gHeader['subs'])
                column_span += n if n > 0 else 1
            # determine which column to select by default
            selection_key, selection_order = None, 0
            for i in range(len(scoreDefs)):
                if (selection_key is None) or (scoreDefs[i].selection_default > selection_order):
                    selection_key, selection_order = scoreDefs[i].key, scoreDefs[i].selection_default

            results.append({ 'label': label, 'headers': headers, 'total_span' : column_span, 'selection_key': selection_key,
                             'scores': scores, 'scoredefs': scoreDefs })

        if len(submissions) > 0:
            # Figure out which submission scores we need to read from the database.
            submission_ids = [id for (id,name) in submissions]
            # not_computed_scoredefs: map (scoredef.id, scoredef) to keep track of non-computed scoredefs
            not_computed_scoredefs = {}
            computed_scoredef_ids = []
            # computed_deps: maps id of a computed scoredef to a list of ids for scoredefs which are
            #                input to the computation
            computed_deps = {}
            for result in results:
                for sdef in result['scoredefs']:
                    if sdef.computed is True:
                        computed_scoredef_ids.append(sdef.id)
                    else:
                        not_computed_scoredefs[sdef.id] = sdef
                if len(computed_scoredef_ids) > 0:
                    computed_ids = SubmissionComputedScore.objects.filter(scoredef_id__in=computed_scoredef_ids).values_list('id')
                    fields = SubmissionComputedScoreField.objects.filter(computed_id__in=computed_ids).select_related('scoredef', 'computed')
                    for field in fields:
                        if not field.scoredef.computed:
                            not_computed_scoredefs[field.scoredef.id] = field.scoredef
                        if field.computed.scoredef_id not in computed_deps:
                            computed_deps[field.computed.scoredef_id] = []
                        computed_deps[field.computed.scoredef_id].append(field.scoredef)
            # Now read the submission scores
            values = {}
            scoredef_ids = [sdef_id for (sdef_id, sdef) in not_computed_scoredefs.iteritems()]
            for s in SubmissionScore.objects.filter(scoredef_id__in=scoredef_ids, result_id__in=submission_ids):
                if s.scoredef_id not in values:
                    values[s.scoredef_id] = {}
                values[s.scoredef_id][s.result_id] = s.value

            # rank values per scoredef.key (not computed)
            ranks = {}
            for (sdef_id, v) in values.iteritems():
                sdef = not_computed_scoredefs[sdef_id]
                ranks[sdef_id] = self.rank_values(submission_ids, v, sort_ascending=sdef.sorting=='asc')

            # compute values for computed scoredefs
            for result in results:
                for sdef in result['scoredefs']:
                    if sdef.computed:
                        operation = getattr(models, sdef.computed_score.operation)
                        if (operation.name == 'Avg'):
                            cnt = len(computed_deps[sdef.id])
                            if (cnt > 0):
                                computed_values = {}
                                for id in submission_ids:
                                    computed_values[id] = sum([ranks[d.id][id] for d in computed_deps[sdef.id]]) / float(cnt)
                                values[sdef.id] = computed_values
                                ranks[sdef.id] = self.rank_values(submission_ids, computed_values, sort_ascending=sdef.sorting=='asc')

            #format values
            for result in results:
                scores = result['scores']
                for sdef in result['scoredefs']:
                    knownValues = {}
                    if sdef.id in values:
                        knownValues = values[sdef.id]
                    knownRanks = {}
                    if sdef.id in ranks:
                        knownRanks = ranks[sdef.id]
                    for id in submission_ids:
                        v = "-"
                        if id in knownValues:
                            v = CompetitionPhase.format_value(knownValues[id], sdef.numeric_format)
                        r = "-"
                        if id in knownRanks:
                            r = knownRanks[id]
                        if sdef.show_rank:
                            scores[id]['values'].append({'val': v, 'rnk': r, 'name' : sdef.key})
                        else:
                            scores[id]['values'].append({'val': v, 'hidden_rnk': r, 'name' : sdef.key})
                    if (sdef.key == result['selection_key']):
                        overall_ranks = ranks[sdef.id]
                ranked_submissions = sorted(submission_ids, cmp=CompetitionPhase.rank_submissions(overall_ranks))
                final_scores = [(overall_ranks[id], scores[id]) for id in ranked_submissions]
                result['scores'] = final_scores
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
    file_url_base = models.CharField(max_length=2000, blank=True)
    inputfile = models.FileField(upload_to=submission_inputfile_name, storage=BundleStorage, null=True, blank=True)
    runfile = models.FileField(upload_to=submission_runfile_name, storage=BundleStorage, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    execution_key = models.TextField(blank=True, default="")
    status = models.ForeignKey(CompetitionSubmissionStatus)
    status_details = models.CharField(max_length=100, null=True, blank=True)
    submission_number = models.PositiveIntegerField(default=0)
    output_file = models.FileField(upload_to=submission_output_filename, storage=BundleStorage, null=True, blank=True)
    stdout_file = models.FileField(upload_to=submission_stdout_filename, storage=BundleStorage, null=True, blank=True)
    stderr_file = models.FileField(upload_to=submission_stderr_filename, storage=BundleStorage, null=True, blank=True)
    prediction_runfile = models.FileField(upload_to=submission_prediction_runfile_name,
                                          storage=BundleStorage, null=True, blank=True)
    prediction_output_file = models.FileField(upload_to=submission_prediction_output_filename,
                                              storage=BundleStorage, null=True, blank=True)

    class Meta:
        unique_together = (('submission_number','phase','participant'),)

    def __unicode__(self):
        return "%s %s %s %s" % (self.pk, self.phase.competition.title, self.phase.label, self.participant.user.email)

    def save(self,*args,**kwargs):
        print "Saving competition submission."
        if self.participant.competition != self.phase.competition:
            raise Exception("Competition for phase and participant must be the same")

        # only at save on object creation should it be submitted
        if not self.pk:
            print "This is a new submission, getting the submission number."
            subnum = CompetitionSubmission.objects.filter(phase=self.phase, participant=self.participant).aggregate(Max('submission_number'))['submission_number__max']
            if subnum is not None:
                self.submission_number = subnum + 1
            else:
                self.submission_number = 1
            print "This is submission number %d" % self.submission_number

            if (self.submission_number > self.phase.max_submissions):
                print "Checking to see if the submission number (%d) is greater than the maximum allowed (%d)" % (self.submission_number, self.phase.max_submissions)
                raise PermissionDenied("The maximum number of submissions has been reached.")
            else:
                print "Submission number below maximum."

            self.set_status(CompetitionSubmissionStatus.SUBMITTING,force_save=False)

        print "Setting the file url base."
        self.file_url_base = self.file.storage.url('')

        print "Calling super save."
        res = super(CompetitionSubmission,self).save(*args,**kwargs)
        return res

    def set_status(self, status, force_save=False):
        self.status = CompetitionSubmissionStatus.objects.get(codename=status)
        if force_save:
            self.save()

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

class CompetitionDefBundle(models.Model):
    config_bundle = models.FileField(upload_to='competition-bundles', storage=BundleStorage)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner')
    created_at = models.DateTimeField(auto_now_add=True)

    def unpack(self):
        """
        This method unpacks a competition bundle and creates a competition from
        the assets found inside (the competition bundle). The format of the
        competition bundle is described on the CodaLab Wiki:
        https://github.com/codalab/codalab/wiki/12.-Building-a-Competition-Bundle
        """
        # Get the bundle data, which is stored as a zipfile
        logger.info("CompetitionDefBundle::unpack begins (pk=%s)", self.pk)
        zf = zipfile.ZipFile(self.config_bundle)
        logger.debug("CompetitionDefBundle::unpack creating base competition (pk=%s)", self.pk)
        comp_spec_file = [x for x in zf.namelist() if ".yaml" in x ][0]
        comp_spec = yaml.load(zf.open(comp_spec_file))
        comp_base = comp_spec.copy()
        for block in ['html', 'phases', 'leaderboard']:
            if block in comp_base:
                del comp_base[block]
        comp_base['creator'] = self.owner
        comp_base['modified_by'] = self.owner
        if 'end_date' in comp_base:
            if type(comp_base['end_date']) is datetime.datetime.date:
                comp_base['end_date'] = datetime.datetime.combine(comp_base['end_date'], datetime.time())
        comp = Competition(**comp_base)
        comp.save()
        logger.debug("CompetitionDefBundle::unpack created base competition (pk=%s)", self.pk)

        # Unpack and save the logo
        if 'image' in comp_base:
            comp.image.save(comp_base['image'], File(io.BytesIO(zf.read(comp_base['image']))))
            comp.save()
            logger.debug("CompetitionDefBundle::unpack saved competition logo (pk=%s)", self.pk)

        # Populate competition pages
        pc,_ = PageContainer.objects.get_or_create(object_id=comp.id, content_type=ContentType.objects.get_for_model(comp))
        details_category = ContentCategory.objects.get(name="Learn the Details")
        Page.objects.create(category=details_category, container=pc,  codename="overview",
                                   label="Overview", rank=0, html=zf.read(comp_spec['html']['overview']))
        Page.objects.create(category=details_category, container=pc,  codename="evaluation",
                                   label="Evaluation", rank=0, html=zf.read(comp_spec['html']['evaluation']))
        Page.objects.create(category=details_category, container=pc,  codename="terms_and_conditions",
                                   label="Terms and Conditions", rank=0, html=zf.read(comp_spec['html']['terms']))
        participate_category = ContentCategory.objects.get(name="Participate")
        Page.objects.create(category=participate_category, container=pc,  codename="get_data",
                                   label="Get Data", rank=0, html=zf.read(comp_spec['html']['data']))
        Page.objects.create(category=participate_category, container=pc,  codename="submit_results", label="Submit Results", rank=1, html="")
        logger.debug("CompetitionDefBundle::unpack created competition pages (pk=%s)", self.pk)

        # Create phases
        for p_num in comp_spec['phases']:
            phase_spec = comp_spec['phases'][p_num].copy()
            phase_spec['competition'] = comp
            if 'datasets' in phase_spec:
                datasets = phase_spec['datasets']
                del phase_spec['datasets']
            else:
                datasets = {}
            if type(phase_spec['start_date']) is datetime.datetime.date:
                phase_spec['start_date'] = datetime.datetime.combine(phase['start_date'], datetime.time())
            phase, created = CompetitionPhase.objects.get_or_create(**phase_spec)
            logger.debug("CompetitionDefBundle::unpack created phase (pk=%s)", self.pk)
            # Evaluation Program
            phase.scoring_program.save(phase_spec['scoring_program'], File(io.BytesIO(zf.read(phase_spec['scoring_program']))))
            phase.reference_data.save(phase_spec['reference_data'], File(io.BytesIO(zf.read(phase_spec['reference_data']))))
            if 'input_data' in phase_spec:
                phase.input_data.save(phase_spec['input_data'], File(io.BytesIO(zf.read(phase_spec['input_data']))))
            phase.save()
            logger.debug("CompetitionDefBundle::unpack saved scoring program and reference data (pk=%s)", self.pk)
            eft,cr_=ExternalFileType.objects.get_or_create(name="Data", codename="data")
            count = 1
            for ds in datasets.keys():
                f = ExternalFile.objects.create(type=eft, source_url=datasets[ds]['url'], name=datasets[ds]['name'], creator=self.owner)
                f.save()
                d = Dataset.objects.create(creator=self.owner, datafile=f, number=count)
                d.save()
                phase.datasets.add(d)
                phase.save()
                count += 1
            logger.debug("CompetitionDefBundle::unpack saved datasets (pk=%s)", self.pk)

        logger.debug("CompetitionDefBundle::unpack saved created competition phases (pk=%s)", self.pk)

        # Create leaderboard
        if 'leaderboard' in comp_spec:
            # If there's more than one create each of them
            if 'leaderboards' in comp_spec['leaderboard']:
                leaderboards = {}
                for key, value in comp_spec['leaderboard']['leaderboards'].items():
                    rg,cr = SubmissionResultGroup.objects.get_or_create(competition=comp, key=value['label'].strip(), label=value['label'].strip(), ordering=value['rank'])
                    leaderboards[rg.label] = rg
                    for gp in comp.phases.all():
                        rgp,crx = SubmissionResultGroupPhase.objects.get_or_create(phase=gp, group=rg)
            logger.debug("CompetitionDefBundle::unpack created leaderboard (pk=%s)", self.pk)

            # Create score groups
            if 'column_groups' in comp_spec['leaderboard']:
                groups = {}
                for key, vals in comp_spec['leaderboard']['column_groups'].items():
                    if vals is None:
                        vals = dict()
                    s,cr = SubmissionScoreSet.objects.get_or_create(competition=comp, key=key.strip(), defaults=vals)
                    groups[s.label] = s
            logger.debug("CompetitionDefBundle::unpack created score groups (pk=%s)", self.pk)

            # Create scores.
            if 'columns' in comp_spec['leaderboard']:
                columns = {}
                for key, vals in comp_spec['leaderboard']['columns'].items():
                    # Do non-computed columns first
                    if 'computed' in vals:
                        continue
                    sdefaults = {
                                    'label' : "" if 'label' not in vals else vals['label'].strip(),
                                    'numeric_format' : "2" if 'numeric_format' not in vals else vals['numeric_format'],
                                    'show_rank' : True,
                                    'sorting' : 'desc' if 'sort' not in vals else vals['sort']
                                    }
                    if 'selection_default' in vals: 
                        sdefaults['selection_default'] = vals['selection_default']

                    sd,cr = SubmissionScoreDef.objects.get_or_create(
                                competition=comp,
                                key=key,
                                computed=False,
                                defaults=sdefaults)
                    columns[sd.key] = sd

                    # Associate the score definition with its column group
                    if 'column_group' in vals:
                        gparent = groups[vals['column_group']['label']]
                        g,cr = SubmissionScoreSet.objects.get_or_create(
                                competition=comp,
                                parent=gparent,
                                key=sd.key,
                                defaults=dict(scoredef=sd, label=sd.label))
                    else:
                        g,cr = SubmissionScoreSet.objects.get_or_create(
                                competition=comp,
                                key=sd.key,
                                defaults=dict(scoredef=sd, label=sd.label))

                    # Associate the score definition with its leaderboard
                    sdg = SubmissionScoreDefGroup.objects.create(scoredef=sd, group=leaderboards[vals['leaderboard']['label']])

                for key, vals in comp_spec['leaderboard']['columns'].items():
                    # Only process the computed columns this time around.
                    if 'computed' not in vals:
                        continue
                    # Create the score definition
                    is_computed = True
                    sdefaults = {
                                    'label' : "" if 'label' not in vals else vals['label'].strip(),
                                    'numeric_format' : "2" if 'numeric_format' not in vals else vals['numeric_format'],
                                    'show_rank' : not is_computed,
                                    'sorting' : 'desc' if 'sort' not in vals else vals['sort']
                                    }
                    if 'selection_default' in vals:
                        sdefaults['selection_default'] = vals['selection_default']

                    sd,cr = SubmissionScoreDef.objects.get_or_create(
                                competition=comp,
                                key=key,
                                computed=is_computed,
                                defaults=sdefaults)
                    sc,cr = SubmissionComputedScore.objects.get_or_create(scoredef=sd, operation=vals['computed']['operation'])
                    for f in vals['computed']['fields'].split(","):
                        f=f.strip()
                        # Note the lookup in brats_score_defs. The assumption is that computed properties are defined in
                        # brats_leaderboard_defs after the fields they reference.
                        # This is not a safe assumption -- given we can't control key/value ordering in a dictionary.
                        SubmissionComputedScoreField.objects.get_or_create(computed=sc, scoredef=columns[f])
                    columns[sd.key] = sd

                    # Associate the score definition with its column group
                    if 'column_group' in vals:
                        gparent = groups[vals['column_group']['label']]
                        g,cr = SubmissionScoreSet.objects.get_or_create(
                                competition=comp,
                                parent=gparent,
                                key=sd.key,
                                defaults=dict(scoredef=sd, label=sd.label))
                    else:
                        g,cr = SubmissionScoreSet.objects.get_or_create(
                                competition=comp,
                                key=sd.key,
                                defaults=dict(scoredef=sd, label=sd.label))

                    # Associate the score definition with its leaderboard
                    sdg = SubmissionScoreDefGroup.objects.create(scoredef=sd, group=leaderboards[vals['leaderboard']['label']])
                logger.debug("CompetitionDefBundle::unpack created scores (pk=%s)", self.pk)

        # Add owner as participant so they can view the competition
        approved = ParticipantStatus.objects.get(codename=ParticipantStatus.APPROVED)
        resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=self.owner, competition=comp, defaults={'status':approved})
        logger.debug("CompetitionDefBundle::unpack added owner as participant (pk=%s)", self.pk)

        return comp

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
    key = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    scoredef = models.ForeignKey(SubmissionScoreDef,null=True,blank=True)

    class Meta:
        unique_together = (('key','competition'),)

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
