import exceptions
import logging
import random
import operator
import os, io
from os.path import abspath, basename, dirname, join, normpath, split
import zipfile
import yaml
import tempfile
import datetime
import django.dispatch
import time
import string
import uuid
from django.db import models
from django.db import IntegrityError
from django.db.models import Max
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.files.storage import get_storage_class
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from mptt.models import MPTTModel, TreeForeignKey
from pytz import utc
from guardian.shortcuts import assign_perm
from django_extensions.db.fields import UUIDField
from django.contrib.auth import get_user_model


User = get_user_model()
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
    image = models.FileField(upload_to='logos', storage=PublicStorage, null=True, blank=True, verbose_name="Logo")
    image_url_base = models.CharField(max_length=255)
    has_registration = models.BooleanField(default=False, verbose_name="Registration Required")
    end_date = models.DateTimeField(null=True,blank=True, verbose_name="End Date (UTC)")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_creator')
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='competition_admins', blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='competitioninfo_modified_by')
    last_modified = models.DateTimeField(auto_now_add=True)
    pagecontainers = generic.GenericRelation(PageContainer)
    published = models.BooleanField(default=False, verbose_name="Publicly Available")
    # Let's assume the first phase never needs "migration"
    last_phase_migration = models.PositiveIntegerField(default=1)
    is_migrating = models.BooleanField(default=False)
    force_submission_to_leaderboard = models.BooleanField(default=False)
    disallow_leaderboard_modifying = models.BooleanField(default=False)
    secret_key = UUIDField(version=4)
    enable_medical_image_viewer = models.BooleanField(default=False)
    enable_detailed_results = models.BooleanField(default=False)
    original_yaml_file = models.TextField(default='', blank=True, null=True)

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

    def do_phase_migration(self, current_phase, last_phase):
        '''
        Does the actual migrating of submissions from last_phase to current_phase

        current_phase: The new phase object we are entering
        last_phase: The phase object to transfer submissions from
        '''
        logger.info('Doing phase migration on competition pk=%s from phase: %s to phase: %s' %
                    (self.pk, last_phase.phasenumber, current_phase.phasenumber))

        if self.is_migrating:
            logger.info('Trying to migrate competition pk=%s, but it is already being migrated!' % self.pk)
            return

        self.is_migrating = True
        self.save()

        try:
            submissions = []
            leader_board = PhaseLeaderBoard.objects.get(phase=last_phase)

            leader_board_entries = PhaseLeaderBoardEntry.objects.filter(board=leader_board)
            for submission in leader_board_entries:
                submissions.append(submission.result)

            participants = {}

            for s in submissions:
                participants[s.participant] = s

            from tasks import evaluate_submission

            for participant, submission in participants.items():
                logger.info('Moving submission %s over' % submission)

                new_submission = CompetitionSubmission.objects.create(
                    participant=participant,
                    file=submission.file,
                    phase=current_phase
                )

                evaluate_submission(new_submission.pk, current_phase.is_scoring_only)
        except PhaseLeaderBoard.DoesNotExist:
            pass

        current_phase.is_migrated = True
        current_phase.save()

        # TODO: ONLY IF SUCCESSFUL
        self.is_migrating = False # this should really be True until evaluate_submission tasks are all the way completed
        self.last_phase_migration = current_phase.phasenumber
        self.save()

    def check_trailing_phase_submissions(self):
        '''
        Checks that the requested competition has all submissions in the current phase, none trailing in the previous
        phase
        '''
        if self.is_migrating:
            logger.info('Trying to check migrations on competition pk=%s, but it is already being migrated!' % self.pk)
            return

        last_phase = None
        current_phase = None

        for phase in self.phases.all():
            if phase.is_active:
                current_phase = phase
                break

            last_phase = phase

        if current_phase is None or last_phase is None:
            return

        logger.info("Checking for needed migrations on competition pk=%s, last phase: %s, current phase: %s" %
                    (self.pk, last_phase.phasenumber, current_phase.phasenumber))

        if current_phase.phasenumber > self.last_phase_migration:
            if current_phase.auto_migration:
                self.do_phase_migration(current_phase, last_phase)


class Page(models.Model):
    category = TreeForeignKey(ContentCategory)
    defaults = models.ForeignKey(DefaultContentItem, null=True, blank=True)
    codename = models.SlugField(max_length=100)
    container = models.ForeignKey(PageContainer, related_name='pages', verbose_name="Competition")
    title = models.CharField(max_length=100, null=True, blank=True)
    label = models.CharField(max_length=100, verbose_name="Title")
    rank = models.IntegerField(default=0, verbose_name="Order")
    visibility = models.BooleanField(default=True, verbose_name="Visible")
    markup = models.TextField(blank=True)
    html = models.TextField(blank=True, verbose_name="Content")
    competition = models.ForeignKey(Competition, related_name='pages', null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        unique_together = (('label','category','container'),)
        ordering = ['category', 'rank']

    def save(self,*args,**kwargs):
        #if not self.title:
        #    self.title = "%s - %s" % ( self.container.name, self.label )
        if self.defaults:
            if self.category != self.defaults.category:
                raise Exception("Defaults category must match Item category")
            if self.defaults.required and self.visibility is False:
                raise Exception("Item is required and must be visible")
        return super(Page,self).save(*args,**kwargs)

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
    # will generate /competition/1/1/submissions/1/1/
    return os.path.join(
        "competition",
        str(instance.phase.competition.pk),
        str(instance.phase.pk),
        "submissions",
        str(instance.participant.user.pk),
        str(instance.submission_number)
    )

def submission_file_name(instance, filename="predictions.zip"):
    return os.path.join(submission_root(instance), filename)

def submission_inputfile_name(instance, filename="input.txt"):
    return os.path.join(submission_root(instance), filename)

def submission_history_file_name(instance, filename="history.txt"):
    return os.path.join(submission_root(instance), filename)

def submission_runfile_name(instance, filename="run.txt"):
    return os.path.join(submission_root(instance), filename)

def submission_detailed_results_filename(instance, filename="detailed_results.html"):
    return os.path.join(submission_root(instance), "run", "html", filename)

def submission_output_filename(instance, filename="output.zip"):
    return os.path.join(submission_root(instance), "run", filename)

def submission_private_output_filename(instance, filename="private_output.zip"):
    return os.path.join(submission_root(instance), "run", filename)

def submission_stdout_filename(instance, filename="stdout.txt"):
    return os.path.join(submission_root(instance), "run", filename)

def submission_stderr_filename(instance, filename="stderr.txt"):
    return os.path.join(submission_root(instance), "run", filename)

def submission_prediction_runfile_name(instance, filename="run.txt"):
    return os.path.join(submission_root(instance), "pred", filename)

def submission_prediction_output_filename(instance, filename="output.zip"):
    return os.path.join(submission_root(instance), "pred", "run", filename)

class _LeaderboardManagementMode(object):
    """
    Provides a set of constants which define when results become visible to participants
    and how successful submmisions are added to the leaderboard.
    """
    @property
    def DEFAULT(self):
        """
        Specifies that results are visible as soon as they are available and that adding
        a successful submission to the leaderboard is a manual step.
        """
        return 'default'
    @property
    def HIDE_RESULTS(self):
        """
        Specifies that results are hidden from participants until competition owners make
        them visible and that a participant's last successful submission is automatically
        added to the leaderboard.
        """
        return 'hide_results'
    def is_valid(self, mode):
        """Returns true if the given string is a valid constant to define a management mode."""
        return mode == self.DEFAULT or mode == self.HIDE_RESULTS

LeaderboardManagementMode = _LeaderboardManagementMode()

# Competition Phase
class CompetitionPhase(models.Model):
    """
        A phase of a competition.
    """
    COLOR_CHOICES = (
        ('white', 'White'),
        ('orange', 'Orange'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('purple', 'Purple'),
    )

    competition = models.ForeignKey(Competition,related_name='phases')
    description = models.CharField(max_length=1000, null=True, blank=True)
    # Is this 0 based or 1 based?
    phasenumber = models.PositiveIntegerField(verbose_name="Number")
    label = models.CharField(max_length=50, blank=True, verbose_name="Name")
    start_date = models.DateTimeField(verbose_name="Start Date (UTC)")
    max_submissions = models.PositiveIntegerField(default=100, verbose_name="Maximum Submissions (per User)")
    max_submissions_per_day = models.PositiveIntegerField(default=999, verbose_name="Max Submissions (per User) per day")
    is_scoring_only = models.BooleanField(default=True, verbose_name="Results Scoring Only")
    scoring_program = models.FileField(upload_to=phase_scoring_program_file, storage=BundleStorage,null=True,blank=True, verbose_name="Scoring Program")
    reference_data = models.FileField(upload_to=phase_reference_data_file, storage=BundleStorage,null=True,blank=True, verbose_name="Reference Data")
    input_data = models.FileField(upload_to=phase_input_data_file, storage=BundleStorage,null=True,blank=True, verbose_name="Input Data")
    datasets = models.ManyToManyField(Dataset, blank=True, related_name='phase')
    leaderboard_management_mode = models.CharField(max_length=50, default=LeaderboardManagementMode.DEFAULT, verbose_name="Leaderboard Mode")
    auto_migration = models.BooleanField(default=False)
    is_migrated = models.BooleanField(default=False)
    execution_time_limit = models.PositiveIntegerField(default=(5 * 60), verbose_name="Execution time limit (in seconds)")
    color = models.CharField(max_length=24, choices=COLOR_CHOICES, blank=True, null=True)

    input_data_organizer_dataset = models.ForeignKey('OrganizerDataSet', null=True, blank=True, related_name="input_data_organizer_dataset", verbose_name="Input Data", on_delete=models.SET_NULL)
    reference_data_organizer_dataset = models.ForeignKey('OrganizerDataSet', null=True, blank=True, related_name="reference_data_organizer_dataset", verbose_name="Reference Data", on_delete=models.SET_NULL)
    scoring_program_organizer_dataset = models.ForeignKey('OrganizerDataSet', null=True, blank=True, related_name="scoring_program_organizer_dataset", verbose_name="Scoring Program", on_delete=models.SET_NULL)

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

    @property
    def is_blind(self):
        """
        Indicates whether results are always hidden from participants.
        """
        return self.leaderboard_management_mode == LeaderboardManagementMode.HIDE_RESULTS

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
        result_location = []
        lb, created = PhaseLeaderBoard.objects.get_or_create(phase=self)
        if not created:
            qs = PhaseLeaderBoardEntry.objects.filter(board=lb)
            for entry in qs:
                result_location.append(entry.result.file.name)
            for (rid, name) in qs.values_list('result_id', 'result__participant__user__username'):
                submissions.append((rid,  name))

        results = []
        for count, g in enumerate(SubmissionResultGroup.objects.filter(phases__in=[self]).order_by('ordering')):
            label = g.label
            headers = []
            scores = {}

            # add the location of the results on the blob storage to the scores
            for (pk,name) in submissions:
                scores[pk] = {'username': name, 'id': pk, 'values': [], 'resultLocation': result_location[count]}

            scoreDefs = []
            columnKeys = {} # maps a column key to its index in headers list
            for x in SubmissionScoreSet.objects.order_by('tree_id','lft').filter(scoredef__isnull=False,
                                                                        scoredef__groups__in=[g],
                                                                        **kwargs).select_related('scoredef', 'parent'):
                if x.parent is not None:
                    columnKey = x.parent.key
                    columnLabel = x.parent.label
                    columnOrdering = x.parent.ordering
                    columnSubLabels = [{'key': x.key, 'label': x.label, 'ordering': x.ordering}]
                else:
                    columnKey = x.key
                    columnLabel = x.label
                    columnOrdering = x.ordering
                    columnSubLabels = []
                if columnKey not in columnKeys:
                    columnKeys[columnKey] = len(headers)
                    headers.append({'key': columnKey, 'label': columnLabel, 'subs': columnSubLabels, 'ordering': columnOrdering})
                else:
                    headers[columnKeys[columnKey]]['subs'].extend(columnSubLabels)

                scoreDefs.append(x.scoredef)
            # Sort headers appropiately
            def sortkey(x):
                return x['ordering']
            headers.sort(key=sortkey, reverse=False)
            for header in headers:
                header['subs'].sort(key=sortkey, reverse=False)
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
    """
    Represents a submission from a competition participant.
    """
    participant = models.ForeignKey(CompetitionParticipant, related_name='submissions')
    phase = models.ForeignKey(CompetitionPhase, related_name='submissions')
    file = models.FileField(upload_to=submission_file_name, storage=BundleStorage, null=True, blank=True)
    file_url_base = models.CharField(max_length=2000, blank=True)
    description = models.CharField(max_length=256, blank=True)
    inputfile = models.FileField(upload_to=submission_inputfile_name, storage=BundleStorage, null=True, blank=True)
    runfile = models.FileField(upload_to=submission_runfile_name, storage=BundleStorage, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    execution_key = models.TextField(blank=True, default="")
    status = models.ForeignKey(CompetitionSubmissionStatus)
    status_details = models.CharField(max_length=100, null=True, blank=True)
    submission_number = models.PositiveIntegerField(default=0)
    output_file = models.FileField(upload_to=submission_output_filename, storage=BundleStorage, null=True, blank=True)
    private_output_file = models.FileField(upload_to=submission_private_output_filename, storage=BundleStorage, null=True, blank=True)
    stdout_file = models.FileField(upload_to=submission_stdout_filename, storage=BundleStorage, null=True, blank=True)
    stderr_file = models.FileField(upload_to=submission_stderr_filename, storage=BundleStorage, null=True, blank=True)
    history_file = models.FileField(upload_to=submission_history_file_name, storage=BundleStorage, null=True, blank=True)
    detailed_results_file = models.FileField(upload_to=submission_detailed_results_filename, storage=BundleStorage, null=True, blank=True)
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

            if hasattr(self.phase, 'max_submissions_per_day'):
                print 'Checking submissions per day count'

                submissions_from_today_count = len(CompetitionSubmission.objects.filter(
                    phase__competition=self.phase.competition,
                    participant=self.participant,
                    submitted_at__gte=datetime.date.today()
                ))

                print 'Count is %s and maximum is %s' % (submissions_from_today_count, self.phase.max_submissions_per_day)

                if submissions_from_today_count + 1 > self.phase.max_submissions_per_day or self.phase.max_submissions_per_day == 0:
                    print 'PERMISSION DENIED'
                    raise PermissionDenied("The maximum number of submissions this day have been reached.")

            self.status = CompetitionSubmissionStatus.objects.get_or_create(codename=CompetitionSubmissionStatus.SUBMITTING)[0]

        print "Setting the file url base."
        self.file_url_base = self.file.storage.url('')

        print "Calling super save."
        res = super(CompetitionSubmission,self).save(*args,**kwargs)
        return res

    def get_filename(self):
        """
        Returns the short name of the file which was uploaded to create the submission.
        """
        name = ''
        try:
            name = self.file.storage.properties(self.file.name)['x-ms-meta-name']
        except:
            pass
        if len(name) == 0:
            # For backwards compat, fallback to this method of getting the name.
            name = split(self.file.name)[1]
        return name

    def get_file_for_download(self, key, requested_by):
        """
        Returns the FileField object for the file that is to be downloaded by the given user.

        key: A name identifying the file to download. The choices are 'input.zip', 'output.zip',
           'prediction-output.zip', 'stdout.txt', 'stderr.txt', 'history.txt' or 'private_output.zip'
        requested_by: A user object identifying the user making the request to access the file.

        Raises:
           ValueError exception for improper arguments.
           PermissionDenied exception when access to the file cannot be granted.
        """
        downloadable_files = {
            'input.zip': ('file', 'zip', False),
            'output.zip': ('output_file', 'zip', True),
            'private_output.zip': ('private_output_file', 'zip', True),
            'prediction-output.zip': ('prediction_output_file', 'zip', True),
            'stdout.txt': ('stdout_file', 'txt', True),
            'stderr.txt': ('stderr_file', 'txt', False),
            'detailed_results.html': ('detailed_results_file', 'html', True),
        }
        if key not in downloadable_files:
            raise ValueError("File requested is not valid.")
        file_attr, file_ext, file_has_restricted_access = downloadable_files[key]
        # If the user requesting access is the owner, access granted
        if self.participant.competition.creator.id != requested_by.id:
            # User making request must be owner of this submission and be granted
            # download privilege by the competition owners.
            if self.participant.user.id != requested_by.id:
                raise PermissionDenied()
            if file_has_restricted_access and self.phase.is_blind:
                raise PermissionDenied()

        if key == 'private_output.zip':
            if self.participant.competition.creator.id != requested_by.id:
                raise PermissionDenied()

        if file_ext == 'txt':
            file_type = 'text/plain'
        elif file_ext == 'html':
            file_type = 'text/html'
        else:
            file_type = 'application/zip'
        file_name = "{0}-{1}-{2}".format(self.participant.user.username, self.submission_number, key)
        return getattr(self, file_attr), file_type, file_name

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
    ordering = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = (('key','competition'),)

    def __unicode__(self):
        return self.label

class CompetitionDefBundle(models.Model):
    config_bundle = models.FileField(upload_to='competition-bundles', storage=BundleStorage)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner')
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def localize_datetime(dt):
        """
        Returns the given date or datetime as a datetime with tzinfo.
        """
        if type(dt) is str:
            dt = parse_datetime(dt)
        if type(dt) is datetime.date:
            dt = datetime.datetime.combine(dt, datetime.time())
        if not type(dt) is datetime.datetime:
            raise ValueError("Expected a DateTime object but got %s" % dt)
        if dt.tzinfo is None:
            dt = utc.localize(dt)
        return dt

    @transaction.commit_on_success
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
        yaml_contents = zf.open(comp_spec_file).read()

        # Forcing YAML to interpret the file while maintaining the original order things are in
        from collections import OrderedDict
        _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

        def dict_representer(dumper, data):
            return dumper.represent_dict(data.iteritems())

        def dict_constructor(loader, node):
            return OrderedDict(loader.construct_pairs(node))

        yaml.add_representer(OrderedDict, dict_representer)
        yaml.add_constructor(_mapping_tag, dict_constructor)

        comp_spec = yaml.load(yaml_contents)
        comp_base = comp_spec.copy()
        for block in ['html', 'phases', 'leaderboard']:
            if block in comp_base:
                del comp_base[block]
        comp_base['creator'] = self.owner
        comp_base['modified_by'] = self.owner
        comp_base['original_yaml_file'] = yaml_contents

        if 'end_date' in comp_base:
            if comp_base['end_date'] is None:
                del comp_base['end_date']
            else:
                comp_base['end_date'] = CompetitionDefBundle.localize_datetime(comp_base['end_date'])

        admin_names = None
        if 'admin_names' in comp_base:
            admin_names = comp_base['admin_names']
            del comp_base['admin_names']

        comp = Competition(**comp_base)
        comp.save()
        logger.debug("CompetitionDefBundle::unpack created base competition (pk=%s)", self.pk)

        if admin_names:
            logger.debug("CompetitionDefBundle::unpack looking up admins %s", comp_spec['admin_names'])
            admins = User.objects.filter(username__in=admin_names.split(','))
            logger.debug("CompetitionDefBundle::unpack found admins %s", admins)
            comp.admins.add(*admins)

            logger.debug("CompetitionDefBundle::unpack adding admins as participants")
            approved_status = ParticipantStatus.objects.get(codename=ParticipantStatus.APPROVED)

            for admin in admins:
                try:
                    participant = CompetitionParticipant.objects.get(user=admin, competition=comp)
                    participant.status = approved_status
                    participant.save()
                except models.ObjectDoesNotExist:
                    CompetitionParticipant.objects.create(user=admin, competition=comp, status=approved_status)


        # Unpack and save the logo
        if 'image' in comp_base:
            comp.image.save(comp_base['image'], File(io.BytesIO(zf.read(comp_base['image']))))
            comp.save()
            logger.debug("CompetitionDefBundle::unpack saved competition logo (pk=%s)", self.pk)

        # Populate competition pages
        pc,_ = PageContainer.objects.get_or_create(object_id=comp.id, content_type=ContentType.objects.get_for_model(comp))
        details_category = ContentCategory.objects.get(name="Learn the Details")
        Page.objects.create(category=details_category, container=pc,  codename="overview", competition=comp,
                                   label="Overview", rank=0, html=zf.read(comp_spec['html']['overview']))
        Page.objects.create(category=details_category, container=pc,  codename="evaluation", competition=comp,
                                   label="Evaluation", rank=1, html=zf.read(comp_spec['html']['evaluation']))
        Page.objects.create(category=details_category, container=pc,  codename="terms_and_conditions", competition=comp,
                                   label="Terms and Conditions", rank=2, html=zf.read(comp_spec['html']['terms']))

        default_pages = ('overview', 'evaluation', 'terms', 'data')

        for (page_number, (page_name, page_data)) in enumerate(comp_spec['html'].items()):
            if page_name not in default_pages:
                Page.objects.create(
                    category=details_category,
                    container=pc,
                    codename=page_name,
                    competition=comp,
                    label=page_name,
                    rank=3 + page_number,     # Start at 3 (Overview, Evaluation and Terms and Conditions first)
                    html=zf.read(page_data)
                )

                print "%s, %s" % (page_name, page_number)

        participate_category = ContentCategory.objects.get(name="Participate")
        Page.objects.create(category=participate_category, container=pc,  codename="get_data", competition=comp,
                                   label="Get Data", rank=0, html=zf.read(comp_spec['html']['data']))
        Page.objects.create(category=participate_category, container=pc,  codename="submit_results", label="Submit / View Results", rank=1, html="")
        logger.debug("CompetitionDefBundle::unpack created competition pages (pk=%s)", self.pk)

        data_set_cache = {}

        # Create phases
        for index, p_num in enumerate(comp_spec['phases']):
            phase_spec = comp_spec['phases'][p_num].copy()
            phase_spec['competition'] = comp

            if 'leaderboard_management_mode' in phase_spec:
                if not LeaderboardManagementMode.is_valid(phase_spec['leaderboard_management_mode']):
                    msg = "Invalid leaderboard_management_mode ({0}) specified for phase {1}. Reverting to default."
                    logger.warn(msg.format(phase_spec['leaderboard_management_mode'], p_num))
                    phase_spec['leaderboard_management_mode'] = LeaderboardManagementMode.DEFAULT
            else:
                phase_spec['leaderboard_management_mode'] = LeaderboardManagementMode.DEFAULT

            if 'datasets' in phase_spec:
                datasets = phase_spec['datasets']

                for dataset_index, dataset in datasets.items():
                    if "key" in dataset:
                        dataset["url"] = reverse("datasets_download", kwargs={"dataset_key": dataset["key"]})

                del phase_spec['datasets']
            else:
                datasets = {}

            phase_spec['start_date'] = CompetitionDefBundle.localize_datetime(phase_spec['start_date'])

            # First phase can't have auto_migration=True, remove that here
            if index == 0:
                phase_spec['auto_migration'] = False
                comp.last_phase_migration = phase_spec['phasenumber']
                logger.debug('Set last_phase_migration to #%s' % phase_spec['phasenumber'])
                comp.save()

            phase, created = CompetitionPhase.objects.get_or_create(**phase_spec)
            logger.debug("CompetitionDefBundle::unpack created phase (pk=%s)", self.pk)

            # Set default for max submissions per day
            if not hasattr(phase, 'max_submissions_per_day'):
                phase.max_submissions_per_day = 999

            # Create automatic datasets out of some included files, cache file names here as to not make duplicates
            # where many phases use same dataset files
            if hasattr(phase, 'scoring_program') and phase.scoring_program:
                if phase_spec["scoring_program"].endswith(".zip"):
                    phase.scoring_program.save(phase_scoring_program_file(phase), File(io.BytesIO(zf.read(phase_spec['scoring_program']))))

                    file_name = os.path.splitext(os.path.basename(phase_spec['scoring_program']))[0]
                    if phase_spec['scoring_program'] not in data_set_cache:
                        logger.debug('Adding organizer dataset to cache: %s' % phase_spec['scoring_program'])
                        data_set_cache[phase_spec['scoring_program']] = OrganizerDataSet.objects.create(
                            name="%s_%s_%s" % (file_name, phase.phasenumber, comp.pk),
                            type="Scoring Program",
                            data_file=phase.scoring_program.file.name,
                            uploaded_by=self.owner
                        )
                    phase.scoring_program_organizer_dataset = data_set_cache[phase_spec['scoring_program']]
                else:
                    logger.debug("CompetitionDefBundle::unpack getting dataset for scoring_program with key %s", phase_spec["scoring_program"])
                    data_set = OrganizerDataSet.objects.get(key=phase_spec["scoring_program"])
                    phase.scoring_program = data_set.data_file.file.name
                    phase.scoring_program_organizer_dataset = data_set

            if hasattr(phase, 'reference_data') and phase.reference_data:
                if phase_spec["reference_data"].endswith(".zip"):
                    phase.reference_data.save(phase_reference_data_file(phase), File(io.BytesIO(zf.read(phase_spec['reference_data']))))

                    file_name = os.path.splitext(os.path.basename(phase_spec['reference_data']))[0]
                    if phase_spec['reference_data'] not in data_set_cache:
                        logger.debug('Adding organizer dataset to cache: %s' % phase_spec['reference_data'])
                        data_set_cache[phase_spec['reference_data']] = OrganizerDataSet.objects.create(
                            name="%s_%s_%s" % (file_name, phase.phasenumber, comp.pk),
                            type="Reference Data",
                            data_file=phase.reference_data.file.name,
                            uploaded_by=self.owner
                        )
                    phase.reference_data_organizer_dataset = data_set_cache[phase_spec['reference_data']]
                else:
                    logger.debug("CompetitionDefBundle::unpack getting dataset for reference_data with key %s", phase_spec["reference_data"])
                    data_set = OrganizerDataSet.objects.get(key=phase_spec["reference_data"])
                    phase.reference_data = data_set.data_file.file.name
                    phase.reference_data_organizer_dataset = data_set

            if 'input_data' in phase_spec:
                if phase_spec["input_data"].endswith(".zip"):
                    phase.input_data.save(phase_input_data_file(phase), File(io.BytesIO(zf.read(phase_spec['input_data']))))

                    file_name = os.path.splitext(os.path.basename(phase_spec['input_data']))[0]
                    if phase_spec['input_data'] not in data_set_cache:
                        logger.debug('Adding organizer dataset to cache: %s' % phase_spec['input_data'])
                        data_set_cache[phase_spec['input_data']] = OrganizerDataSet.objects.create(
                            name="%s_%s_%s" % (file_name, phase.phasenumber, comp.pk),
                            type="Input Data",
                            data_file=phase.input_data.file.name,
                            uploaded_by=self.owner
                        )
                    phase.input_data_organizer_dataset = data_set_cache[phase_spec['input_data']]
                else:
                    logger.debug("CompetitionDefBundle::unpack getting dataset for input_data with key %s", phase_spec["input_data"])
                    data_set = OrganizerDataSet.objects.get(key=phase_spec["input_data"])
                    phase.input_data = data_set.data_file.file.name
                    phase.input_data_organizer_dataset = data_set

            phase.auto_migration = bool(phase_spec.get('auto_migration', False))
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
                    index = comp_spec['leaderboard']['column_groups'].keys().index(key) + 1
                    if vals is None:
                        vals = dict()
                    setdefaults = {
                        'label' : "" if 'label' not in vals else vals['label'].strip(),
                        'ordering' : index if 'rank' not in vals else vals['rank']
                    }
                    s,cr = SubmissionScoreSet.objects.get_or_create(competition=comp, key=key.strip(), defaults=setdefaults)
                    groups[s.label] = s
            logger.debug("CompetitionDefBundle::unpack created score groups (pk=%s)", self.pk)

            # Create scores.
            if 'columns' in comp_spec['leaderboard']:
                columns = {}
                for key, vals in comp_spec['leaderboard']['columns'].items():
                    index = comp_spec['leaderboard']['columns'].keys().index(key) + 1
                    # Do non-computed columns first
                    if 'computed' in vals:
                        continue
                    sdefaults = {
                                    'label' : "" if 'label' not in vals else vals['label'].strip(),
                                    'numeric_format' : "2" if 'numeric_format' not in vals else vals['numeric_format'],
                                    'show_rank' : True,
                                    'sorting' : 'desc' if 'sort' not in vals else vals['sort'],
                                    'ordering' : index if 'rank' not in vals else vals['rank']
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
                                defaults=dict(scoredef=sd, label=sd.label, ordering=sd.ordering))
                    else:
                        g,cr = SubmissionScoreSet.objects.get_or_create(
                                competition=comp,
                                key=sd.key,
                                defaults=dict(scoredef=sd, label=sd.label, ordering=sd.ordering))

                    # Associate the score definition with its leaderboard
                    sdg = SubmissionScoreDefGroup.objects.create(scoredef=sd, group=leaderboards[vals['leaderboard']['label']])

                for key, vals in comp_spec['leaderboard']['columns'].items():
                    index = comp_spec['leaderboard']['columns'].keys().index(key) + 1
                    # Only process the computed columns this time around.
                    if 'computed' not in vals:
                        continue
                    # Create the score definition
                    is_computed = True
                    sdefaults = {
                                    'label' : "" if 'label' not in vals else vals['label'].strip(),
                                    'numeric_format' : "2" if 'numeric_format' not in vals else vals['numeric_format'],
                                    'show_rank' : not is_computed,
                                    'sorting' : 'desc' if 'sort' not in vals else vals['sort'],
                                    'ordering' : index if 'rank' not in vals else vals['rank']
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
                                defaults=dict(scoredef=sd, label=sd.label, ordering=sd.ordering))
                    else:
                        g,cr = SubmissionScoreSet.objects.get_or_create(
                                competition=comp,
                                key=sd.key,
                                defaults=dict(scoredef=sd, label=sd.label, ordering=sd.ordering))

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
    ordering = models.PositiveIntegerField(default=1)

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
        if self.scoredef.computed is True and self.value:
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


def dataset_data_file(dataset, filename="data.zip"):
    return os.path.join("datasets", str(dataset.pk), str(uuid.uuid4()), filename)


class OrganizerDataSet(models.Model):
    TYPES = (
        ("Reference Data", "Reference Data"),
        ("Scoring Program", "Scoring Program"),
        ("Input Data", "Input Data"),
        ("None", "None")
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=64, choices=TYPES, default="None")
    description = models.TextField(null=True, blank=True)
    data_file = models.FileField(
        upload_to=dataset_data_file,
        storage=BundleStorage,
        verbose_name="Data file",
        blank=True,
        null=True,
    )
    sub_data_files = models.ManyToManyField('OrganizerDataSet', null=True, blank=True, verbose_name="Bundle of data files")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    key = UUIDField(version=4)

    def save(self, **kwargs):
        if self.key is None or self.key == '':
            self.key = "%s" % (uuid.uuid4())
        super(OrganizerDataSet, self).save(**kwargs)

    def __unicode__(self):
        return "%s uploaded by %s" % (self.name, self.uploaded_by)


def add_submission_to_leaderboard(submission):
    """
    Adds the given submission to its leaderboard. It is the caller responsiblity to make
    sure the submission is ready to be added (e.g. it's in the finished state).
    """
    lb, _ = PhaseLeaderBoard.objects.get_or_create(phase=submission.phase)

    logger.info('Adding submission %s to leaderboard %s' % (submission, lb))

    # Currently we only allow one submission into the leaderboard although the leaderboard
    # is setup to accept multiple submissions from the same participant.
    entries = PhaseLeaderBoardEntry.objects.filter(board=lb, result__participant=submission.participant)
    for entry in entries:
        entry.delete()
    lbe, created = PhaseLeaderBoardEntry.objects.get_or_create(board=lb, result=submission)
    return lbe, created
