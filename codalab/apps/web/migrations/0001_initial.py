# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContentVisibility'
        db.create_table(u'web_contentvisibility', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('codename', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20)),
            ('classname', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['ContentVisibility'])

        # Adding model 'ContentCategory'
        db.create_table(u'web_contentcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['web.ContentCategory'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('codename', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('visibility', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ContentVisibility'])),
            ('is_menu', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('content_limit', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'web', ['ContentCategory'])

        # Adding model 'DefaultContentItem'
        db.create_table(u'web_defaultcontentitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('mptt.fields.TreeForeignKey')(to=orm['web.ContentCategory'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('codename', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('initial_visibility', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ContentVisibility'])),
        ))
        db.send_create_signal(u'web', ['DefaultContentItem'])

        # Adding model 'PageContainer'
        db.create_table(u'web_pagecontainer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'web', ['PageContainer'])

        # Adding unique constraint on 'PageContainer', fields ['object_id', 'content_type']
        db.create_unique(u'web_pagecontainer', ['object_id', 'content_type_id'])

        # Adding model 'Page'
        db.create_table(u'web_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('mptt.fields.TreeForeignKey')(to=orm['web.ContentCategory'])),
            ('defaults', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.DefaultContentItem'], null=True, blank=True)),
            ('codename', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('container', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', to=orm['web.PageContainer'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('visibility', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('markup', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'web', ['Page'])

        # Adding unique constraint on 'Page', fields ['label', 'category', 'container']
        db.create_unique(u'web_page', ['label', 'category_id', 'container_id'])

        # Adding model 'ExternalFileType'
        db.create_table(u'web_externalfiletype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('codename', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20)),
        ))
        db.send_create_signal(u'web', ['ExternalFileType'])

        # Adding model 'ExternalFileSource'
        db.create_table(u'web_externalfilesource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('codename', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('service_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['ExternalFileSource'])

        # Adding model 'ExternalFile'
        db.create_table(u'web_externalfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ExternalFileType'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authenz.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('source_address_info', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'web', ['ExternalFile'])

        # Adding model 'ParticipantStatus'
        db.create_table(u'web_participantstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'web', ['ParticipantStatus'])

        # Adding model 'Competition'
        db.create_table(u'web_competition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('image_url_base', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('has_registration', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competitioninfo_creator', to=orm['authenz.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competitioninfo_modified_by', to=orm['authenz.User'])),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'web', ['Competition'])

        # Adding model 'Dataset'
        db.create_table(u'web_dataset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datasets', to=orm['authenz.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('datafile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ExternalFile'])),
        ))
        db.send_create_signal(u'web', ['Dataset'])

        # Adding model 'CompetitionPhase'
        db.create_table(u'web_competitionphase', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(related_name='phases', to=orm['web.Competition'])),
            ('phasenumber', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('max_submissions', self.gf('django.db.models.fields.PositiveIntegerField')(default=100)),
            ('is_scoring_only', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('scoring_program', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('reference_data', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('input_data', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['CompetitionPhase'])

        # Adding M2M table for field datasets on 'CompetitionPhase'
        m2m_table_name = db.shorten_name(u'web_competitionphase_datasets')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('competitionphase', models.ForeignKey(orm[u'web.competitionphase'], null=False)),
            ('dataset', models.ForeignKey(orm[u'web.dataset'], null=False))
        ))
        db.create_unique(m2m_table_name, ['competitionphase_id', 'dataset_id'])

        # Adding model 'CompetitionParticipant'
        db.create_table(u'web_competitionparticipant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='participation', to=orm['authenz.User'])),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(related_name='participants', to=orm['web.Competition'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ParticipantStatus'])),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['CompetitionParticipant'])

        # Adding unique constraint on 'CompetitionParticipant', fields ['user', 'competition']
        db.create_unique(u'web_competitionparticipant', ['user_id', 'competition_id'])

        # Adding model 'CompetitionSubmissionStatus'
        db.create_table(u'web_competitionsubmissionstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('codename', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=20)),
        ))
        db.send_create_signal(u'web', ['CompetitionSubmissionStatus'])

        # Adding model 'CompetitionSubmission'
        db.create_table(u'web_competitionsubmission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='submissions', to=orm['web.CompetitionParticipant'])),
            ('phase', self.gf('django.db.models.fields.related.ForeignKey')(related_name='submissions', to=orm['web.CompetitionPhase'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('file_url_base', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('inputfile', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('runfile', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('submitted_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('execution_key', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.CompetitionSubmissionStatus'])),
            ('status_details', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('submission_number', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('output_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('stdout_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('stderr_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['CompetitionSubmission'])

        # Adding unique constraint on 'CompetitionSubmission', fields ['submission_number', 'phase', 'participant']
        db.create_unique(u'web_competitionsubmission', ['submission_number', 'phase_id', 'participant_id'])

        # Adding model 'SubmissionResultGroup'
        db.create_table(u'web_submissionresultgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Competition'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ordering', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'web', ['SubmissionResultGroup'])

        # Adding model 'SubmissionResultGroupPhase'
        db.create_table(u'web_submissionresultgroupphase', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.SubmissionResultGroup'])),
            ('phase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.CompetitionPhase'])),
        ))
        db.send_create_signal(u'web', ['SubmissionResultGroupPhase'])

        # Adding unique constraint on 'SubmissionResultGroupPhase', fields ['group', 'phase']
        db.create_unique(u'web_submissionresultgroupphase', ['group_id', 'phase_id'])

        # Adding model 'SubmissionScoreDef'
        db.create_table(u'web_submissionscoredef', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Competition'])),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sorting', self.gf('django.db.models.fields.SlugField')(default='asc', max_length=20)),
            ('numeric_format', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('show_rank', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('selection_default', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('computed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'web', ['SubmissionScoreDef'])

        # Adding unique constraint on 'SubmissionScoreDef', fields ['key', 'competition']
        db.create_unique(u'web_submissionscoredef', ['key', 'competition_id'])

        # Adding model 'CompetitionDefBundle'
        db.create_table(u'web_competitiondefbundle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('config_bundle', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner', to=orm['authenz.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'web', ['CompetitionDefBundle'])

        # Adding model 'SubmissionScoreDefGroup'
        db.create_table(u'web_submissionscoredefgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scoredef', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.SubmissionScoreDef'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.SubmissionResultGroup'])),
        ))
        db.send_create_signal(u'web', ['SubmissionScoreDefGroup'])

        # Adding unique constraint on 'SubmissionScoreDefGroup', fields ['scoredef', 'group']
        db.create_unique(u'web_submissionscoredefgroup', ['scoredef_id', 'group_id'])

        # Adding model 'SubmissionComputedScore'
        db.create_table(u'web_submissioncomputedscore', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scoredef', self.gf('django.db.models.fields.related.OneToOneField')(related_name='computed_score', unique=True, to=orm['web.SubmissionScoreDef'])),
            ('operation', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'web', ['SubmissionComputedScore'])

        # Adding model 'SubmissionComputedScoreField'
        db.create_table(u'web_submissioncomputedscorefield', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('computed', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['web.SubmissionComputedScore'])),
            ('scoredef', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.SubmissionScoreDef'])),
        ))
        db.send_create_signal(u'web', ['SubmissionComputedScoreField'])

        # Adding model 'SubmissionScoreSet'
        db.create_table(u'web_submissionscoreset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['web.SubmissionScoreSet'])),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Competition'])),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('scoredef', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.SubmissionScoreDef'], null=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'web', ['SubmissionScoreSet'])

        # Adding model 'SubmissionScore'
        db.create_table(u'web_submissionscore', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(related_name='scores', to=orm['web.CompetitionSubmission'])),
            ('scoredef', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.SubmissionScoreDef'])),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=10)),
        ))
        db.send_create_signal(u'web', ['SubmissionScore'])

        # Adding unique constraint on 'SubmissionScore', fields ['result', 'scoredef']
        db.create_unique(u'web_submissionscore', ['result_id', 'scoredef_id'])

        # Adding model 'PhaseLeaderBoard'
        db.create_table(u'web_phaseleaderboard', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phase', self.gf('django.db.models.fields.related.OneToOneField')(related_name='board', unique=True, to=orm['web.CompetitionPhase'])),
        ))
        db.send_create_signal(u'web', ['PhaseLeaderBoard'])

        # Adding model 'PhaseLeaderBoardEntry'
        db.create_table(u'web_phaseleaderboardentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('board', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entries', to=orm['web.PhaseLeaderBoard'])),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(related_name='leaderboard_entry_result', to=orm['web.CompetitionSubmission'])),
        ))
        db.send_create_signal(u'web', ['PhaseLeaderBoardEntry'])

        # Adding unique constraint on 'PhaseLeaderBoardEntry', fields ['board', 'result']
        db.create_unique(u'web_phaseleaderboardentry', ['board_id', 'result_id'])

        # Adding model 'Bundle'
        db.create_table(u'web_bundle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('inputpath', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('outputpath', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('metadata', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'web', ['Bundle'])

        # Adding model 'Run'
        db.create_table(u'web_run', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bundle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.Bundle'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('metadata', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('programPath', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('inputPath', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('outputPath', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('cellout', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'web', ['Run'])


    def backwards(self, orm):
        # Removing unique constraint on 'PhaseLeaderBoardEntry', fields ['board', 'result']
        db.delete_unique(u'web_phaseleaderboardentry', ['board_id', 'result_id'])

        # Removing unique constraint on 'SubmissionScore', fields ['result', 'scoredef']
        db.delete_unique(u'web_submissionscore', ['result_id', 'scoredef_id'])

        # Removing unique constraint on 'SubmissionScoreDefGroup', fields ['scoredef', 'group']
        db.delete_unique(u'web_submissionscoredefgroup', ['scoredef_id', 'group_id'])

        # Removing unique constraint on 'SubmissionScoreDef', fields ['key', 'competition']
        db.delete_unique(u'web_submissionscoredef', ['key', 'competition_id'])

        # Removing unique constraint on 'SubmissionResultGroupPhase', fields ['group', 'phase']
        db.delete_unique(u'web_submissionresultgroupphase', ['group_id', 'phase_id'])

        # Removing unique constraint on 'CompetitionSubmission', fields ['submission_number', 'phase', 'participant']
        db.delete_unique(u'web_competitionsubmission', ['submission_number', 'phase_id', 'participant_id'])

        # Removing unique constraint on 'CompetitionParticipant', fields ['user', 'competition']
        db.delete_unique(u'web_competitionparticipant', ['user_id', 'competition_id'])

        # Removing unique constraint on 'Page', fields ['label', 'category', 'container']
        db.delete_unique(u'web_page', ['label', 'category_id', 'container_id'])

        # Removing unique constraint on 'PageContainer', fields ['object_id', 'content_type']
        db.delete_unique(u'web_pagecontainer', ['object_id', 'content_type_id'])

        # Deleting model 'ContentVisibility'
        db.delete_table(u'web_contentvisibility')

        # Deleting model 'ContentCategory'
        db.delete_table(u'web_contentcategory')

        # Deleting model 'DefaultContentItem'
        db.delete_table(u'web_defaultcontentitem')

        # Deleting model 'PageContainer'
        db.delete_table(u'web_pagecontainer')

        # Deleting model 'Page'
        db.delete_table(u'web_page')

        # Deleting model 'ExternalFileType'
        db.delete_table(u'web_externalfiletype')

        # Deleting model 'ExternalFileSource'
        db.delete_table(u'web_externalfilesource')

        # Deleting model 'ExternalFile'
        db.delete_table(u'web_externalfile')

        # Deleting model 'ParticipantStatus'
        db.delete_table(u'web_participantstatus')

        # Deleting model 'Competition'
        db.delete_table(u'web_competition')

        # Deleting model 'Dataset'
        db.delete_table(u'web_dataset')

        # Deleting model 'CompetitionPhase'
        db.delete_table(u'web_competitionphase')

        # Removing M2M table for field datasets on 'CompetitionPhase'
        db.delete_table(db.shorten_name(u'web_competitionphase_datasets'))

        # Deleting model 'CompetitionParticipant'
        db.delete_table(u'web_competitionparticipant')

        # Deleting model 'CompetitionSubmissionStatus'
        db.delete_table(u'web_competitionsubmissionstatus')

        # Deleting model 'CompetitionSubmission'
        db.delete_table(u'web_competitionsubmission')

        # Deleting model 'SubmissionResultGroup'
        db.delete_table(u'web_submissionresultgroup')

        # Deleting model 'SubmissionResultGroupPhase'
        db.delete_table(u'web_submissionresultgroupphase')

        # Deleting model 'SubmissionScoreDef'
        db.delete_table(u'web_submissionscoredef')

        # Deleting model 'CompetitionDefBundle'
        db.delete_table(u'web_competitiondefbundle')

        # Deleting model 'SubmissionScoreDefGroup'
        db.delete_table(u'web_submissionscoredefgroup')

        # Deleting model 'SubmissionComputedScore'
        db.delete_table(u'web_submissioncomputedscore')

        # Deleting model 'SubmissionComputedScoreField'
        db.delete_table(u'web_submissioncomputedscorefield')

        # Deleting model 'SubmissionScoreSet'
        db.delete_table(u'web_submissionscoreset')

        # Deleting model 'SubmissionScore'
        db.delete_table(u'web_submissionscore')

        # Deleting model 'PhaseLeaderBoard'
        db.delete_table(u'web_phaseleaderboard')

        # Deleting model 'PhaseLeaderBoardEntry'
        db.delete_table(u'web_phaseleaderboardentry')

        # Deleting model 'Bundle'
        db.delete_table(u'web_bundle')

        # Deleting model 'Run'
        db.delete_table(u'web_run')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'authenz.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'web.bundle': {
            'Meta': {'ordering': "['name']", 'object_name': 'Bundle'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inputpath': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'metadata': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'outputpath': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'web.competition': {
            'Meta': {'ordering': "['end_date']", 'object_name': 'Competition'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitioninfo_creator'", 'to': u"orm['authenz.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'has_registration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_url_base': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitioninfo_modified_by'", 'to': u"orm['authenz.User']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'web.competitiondefbundle': {
            'Meta': {'object_name': 'CompetitionDefBundle'},
            'config_bundle': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': u"orm['authenz.User']"})
        },
        u'web.competitionparticipant': {
            'Meta': {'unique_together': "(('user', 'competition'),)", 'object_name': 'CompetitionParticipant'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'participants'", 'to': u"orm['web.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ParticipantStatus']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'participation'", 'to': u"orm['authenz.User']"})
        },
        u'web.competitionphase': {
            'Meta': {'ordering': "['phasenumber']", 'object_name': 'CompetitionPhase'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'phases'", 'to': u"orm['web.Competition']"}),
            'datasets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'phase'", 'blank': 'True', 'to': u"orm['web.Dataset']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_scoring_only': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'max_submissions': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'phasenumber': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reference_data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'scoring_program': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'web.competitionsubmission': {
            'Meta': {'unique_together': "(('submission_number', 'phase', 'participant'),)", 'object_name': 'CompetitionSubmission'},
            'execution_key': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'file_url_base': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inputfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'output_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submissions'", 'to': u"orm['web.CompetitionParticipant']"}),
            'phase': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submissions'", 'to': u"orm['web.CompetitionPhase']"}),
            'runfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.CompetitionSubmissionStatus']"}),
            'status_details': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'stderr_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'stdout_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'submission_number': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'submitted_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'web.competitionsubmissionstatus': {
            'Meta': {'object_name': 'CompetitionSubmissionStatus'},
            'codename': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'web.contentcategory': {
            'Meta': {'object_name': 'ContentCategory'},
            'codename': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'content_limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_menu': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['web.ContentCategory']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'visibility': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ContentVisibility']"})
        },
        u'web.contentvisibility': {
            'Meta': {'object_name': 'ContentVisibility'},
            'classname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'codename': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'web.dataset': {
            'Meta': {'ordering': "['number']", 'object_name': 'Dataset'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datasets'", 'to': u"orm['authenz.User']"}),
            'datafile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ExternalFile']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'web.defaultcontentitem': {
            'Meta': {'object_name': 'DefaultContentItem'},
            'category': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['web.ContentCategory']"}),
            'codename': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_visibility': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ContentVisibility']"}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'web.externalfile': {
            'Meta': {'object_name': 'ExternalFile'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authenz.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source_address_info': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ExternalFileType']"})
        },
        u'web.externalfilesource': {
            'Meta': {'object_name': 'ExternalFileSource'},
            'codename': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'service_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'web.externalfiletype': {
            'Meta': {'object_name': 'ExternalFileType'},
            'codename': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'web.page': {
            'Meta': {'ordering': "['rank']", 'unique_together': "(('label', 'category', 'container'),)", 'object_name': 'Page'},
            'category': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['web.ContentCategory']"}),
            'codename': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': u"orm['web.PageContainer']"}),
            'defaults': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.DefaultContentItem']", 'null': 'True', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'markup': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'visibility': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'web.pagecontainer': {
            'Meta': {'unique_together': "(('object_id', 'content_type'),)", 'object_name': 'PageContainer'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'web.participantstatus': {
            'Meta': {'object_name': 'ParticipantStatus'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'web.phaseleaderboard': {
            'Meta': {'object_name': 'PhaseLeaderBoard'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phase': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'board'", 'unique': 'True', 'to': u"orm['web.CompetitionPhase']"})
        },
        u'web.phaseleaderboardentry': {
            'Meta': {'unique_together': "(('board', 'result'),)", 'object_name': 'PhaseLeaderBoardEntry'},
            'board': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['web.PhaseLeaderBoard']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'leaderboard_entry_result'", 'to': u"orm['web.CompetitionSubmission']"})
        },
        u'web.run': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Run'},
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Bundle']"}),
            'cellout': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inputPath': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'metadata': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'outputPath': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'programPath': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'web.submissioncomputedscore': {
            'Meta': {'object_name': 'SubmissionComputedScore'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'scoredef': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'computed_score'", 'unique': 'True', 'to': u"orm['web.SubmissionScoreDef']"})
        },
        u'web.submissioncomputedscorefield': {
            'Meta': {'object_name': 'SubmissionComputedScoreField'},
            'computed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['web.SubmissionComputedScore']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scoredef': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.SubmissionScoreDef']"})
        },
        u'web.submissionresultgroup': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'SubmissionResultGroup'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ordering': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'phases': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['web.CompetitionPhase']", 'through': u"orm['web.SubmissionResultGroupPhase']", 'symmetrical': 'False'})
        },
        u'web.submissionresultgroupphase': {
            'Meta': {'unique_together': "(('group', 'phase'),)", 'object_name': 'SubmissionResultGroupPhase'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.SubmissionResultGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.CompetitionPhase']"})
        },
        u'web.submissionscore': {
            'Meta': {'unique_together': "(('result', 'scoredef'),)", 'object_name': 'SubmissionScore'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scores'", 'to': u"orm['web.CompetitionSubmission']"}),
            'scoredef': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.SubmissionScoreDef']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '10'})
        },
        u'web.submissionscoredef': {
            'Meta': {'unique_together': "(('key', 'competition'),)", 'object_name': 'SubmissionScoreDef'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Competition']"}),
            'computed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['web.SubmissionResultGroup']", 'through': u"orm['web.SubmissionScoreDefGroup']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'numeric_format': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'selection_default': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_rank': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sorting': ('django.db.models.fields.SlugField', [], {'default': "'asc'", 'max_length': '20'})
        },
        u'web.submissionscoredefgroup': {
            'Meta': {'unique_together': "(('scoredef', 'group'),)", 'object_name': 'SubmissionScoreDefGroup'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.SubmissionResultGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scoredef': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.SubmissionScoreDef']"})
        },
        u'web.submissionscoreset': {
            'Meta': {'object_name': 'SubmissionScoreSet'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['web.SubmissionScoreSet']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'scoredef': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.SubmissionScoreDef']", 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['web']