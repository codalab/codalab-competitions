# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Team'
        db.create_table(u'teams_team', (
            ('teamId', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('avatar', self.gf('sorl.thumbnail.fields.ImageField')(default='', max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'teams', ['Team'])

        # Adding model 'Membership'
        db.create_table(u'teams_membership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authenz.ClUser'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Team'])),
            ('isAdmin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dateJoined', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('userAccepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('teamAccepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('membershipRequestMessage', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'teams', ['Membership'])

        # Adding unique constraint on 'Membership', fields ['team', 'user']
        db.create_unique(u'teams_membership', ['team_id', 'user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Membership', fields ['team', 'user']
        db.delete_unique(u'teams_membership', ['team_id', 'user_id'])

        # Deleting model 'Team'
        db.delete_table(u'teams_team')

        # Deleting model 'Membership'
        db.delete_table(u'teams_membership')


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
        u'authenz.cluser': {
            'Meta': {'object_name': 'ClUser'},
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
            'organizer_direct_message_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'organizer_status_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'participation_status_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
        u'teams.membership': {
            'Meta': {'unique_together': "(('team', 'user'),)", 'object_name': 'Membership'},
            'dateJoined': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isAdmin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'membershipRequestMessage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authenz.ClUser']"}),
            'teamAccepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teams.Team']"}),
            'userAccepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'teams.team': {
            'Meta': {'object_name': 'Team'},
            'avatar': ('sorl.thumbnail.fields.ImageField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['authenz.ClUser']", 'through': u"orm['teams.Membership']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'teamId': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['teams']