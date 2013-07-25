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

        # Adding model 'ContentContainerType'
        db.create_table(u'web_contentcontainertype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('codename', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'web', ['ContentContainerType'])

        # Adding model 'ContentContainer'
        db.create_table(u'web_contentcontainer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ContentContainerType'], unique=True)),
        ))
        db.send_create_signal(u'web', ['ContentContainer'])

        # Adding model 'ContentEntity'
        db.create_table(u'web_contententity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['web.ContentEntity'])),
            ('container', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entities', to=orm['web.ContentContainer'])),
            ('visibility', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ContentVisibility'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('codename', self.gf('django.db.models.fields.SlugField')(max_length=81, null=True, blank=True)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_items', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'web', ['ContentEntity'])

        # Adding unique constraint on 'ContentEntity', fields ['label', 'container']
        db.create_unique(u'web_contententity', ['label', 'container_id'])

        # Adding model 'PageContainer'
        db.create_table(u'web_pagecontainer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entity', self.gf('mptt.fields.TreeForeignKey')(to=orm['web.ContentEntity'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'web', ['PageContainer'])

        # Adding unique constraint on 'PageContainer', fields ['object_id', 'content_type', 'entity']
        db.create_unique(u'web_pagecontainer', ['object_id', 'content_type_id', 'entity_id'])

        # Adding model 'Page'
        db.create_table(u'web_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pagecontainer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', to=orm['web.PageContainer'])),
            ('rank', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('markup', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'web', ['Page'])

        # Adding model 'ExternalFileType'
        db.create_table(u'web_externalfiletype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('codename', self.gf('django.db.models.fields.SlugField')(max_length=20)),
        ))
        db.send_create_signal(u'web', ['ExternalFileType'])

        # Adding model 'ExternalFileSource'
        db.create_table(u'web_externalfilesource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('codename', self.gf('django.db.models.fields.SlugField')(max_length=50)),
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
            ('codename', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'web', ['ParticipantStatus'])

        # Adding model 'Competition'
        db.create_table(u'web_competition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('has_registration', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competitioninfo_creator', to=orm['authenz.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competitioninfo_modified_by', to=orm['authenz.User'])),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
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
            ('codename', self.gf('django.db.models.fields.SlugField')(max_length=20)),
        ))
        db.send_create_signal(u'web', ['CompetitionSubmissionStatus'])

        # Adding model 'CompetitionSubmission'
        db.create_table(u'web_competitionsubmission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.CompetitionParticipant'])),
            ('phase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.CompetitionPhase'])),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.ExternalFile'])),
            ('submitted_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.CompetitionSubmissionStatus'])),
            ('status_details', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'web', ['CompetitionSubmission'])

        # Adding model 'CompetitionSubmissionResults'
        db.create_table(u'web_competitionsubmissionresults', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['web.CompetitionSubmission'])),
            ('payload', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'web', ['CompetitionSubmissionResults'])


    def backwards(self, orm):
        # Removing unique constraint on 'CompetitionParticipant', fields ['user', 'competition']
        db.delete_unique(u'web_competitionparticipant', ['user_id', 'competition_id'])

        # Removing unique constraint on 'PageContainer', fields ['object_id', 'content_type', 'entity']
        db.delete_unique(u'web_pagecontainer', ['object_id', 'content_type_id', 'entity_id'])

        # Removing unique constraint on 'ContentEntity', fields ['label', 'container']
        db.delete_unique(u'web_contententity', ['label', 'container_id'])

        # Deleting model 'ContentVisibility'
        db.delete_table(u'web_contentvisibility')

        # Deleting model 'ContentContainerType'
        db.delete_table(u'web_contentcontainertype')

        # Deleting model 'ContentContainer'
        db.delete_table(u'web_contentcontainer')

        # Deleting model 'ContentEntity'
        db.delete_table(u'web_contententity')

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

        # Deleting model 'CompetitionSubmissionResults'
        db.delete_table(u'web_competitionsubmissionresults')


    models = {
        u'authenz.user': {
            'Meta': {'object_name': 'User'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'home_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'web.competition': {
            'Meta': {'ordering': "['end_date']", 'object_name': 'Competition'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitioninfo_creator'", 'to': u"orm['authenz.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'has_registration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitioninfo_modified_by'", 'to': u"orm['authenz.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'max_submissions': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'phasenumber': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'web.competitionsubmission': {
            'Meta': {'object_name': 'CompetitionSubmission'},
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ExternalFile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.CompetitionParticipant']"}),
            'phase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.CompetitionPhase']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.CompetitionSubmissionStatus']"}),
            'status_details': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'submitted_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'web.competitionsubmissionresults': {
            'Meta': {'object_name': 'CompetitionSubmissionResults'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payload': ('django.db.models.fields.TextField', [], {}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.CompetitionSubmission']"})
        },
        u'web.competitionsubmissionstatus': {
            'Meta': {'object_name': 'CompetitionSubmissionStatus'},
            'codename': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'web.contentcontainer': {
            'Meta': {'object_name': 'ContentContainer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.ContentContainerType']", 'unique': 'True'})
        },
        u'web.contentcontainertype': {
            'Meta': {'object_name': 'ContentContainerType'},
            'codename': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'web.contententity': {
            'Meta': {'ordering': "['rank']", 'unique_together': "(('label', 'container'),)", 'object_name': 'ContentEntity'},
            'codename': ('django.db.models.fields.SlugField', [], {'max_length': '81', 'null': 'True', 'blank': 'True'}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entities'", 'to': u"orm['web.ContentContainer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'max_items': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['web.ContentEntity']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'codename': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'service_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'web.externalfiletype': {
            'Meta': {'object_name': 'ExternalFileType'},
            'codename': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'web.page': {
            'Meta': {'ordering': "['rank']", 'object_name': 'Page'},
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pagecontainer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': u"orm['web.PageContainer']"}),
            'rank': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'web.pagecontainer': {
            'Meta': {'unique_together': "(('object_id', 'content_type', 'entity'),)", 'object_name': 'PageContainer'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'entity': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['web.ContentEntity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'web.participantstatus': {
            'Meta': {'object_name': 'ParticipantStatus'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['web']