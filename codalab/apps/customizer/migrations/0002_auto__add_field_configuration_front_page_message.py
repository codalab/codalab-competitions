# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Configuration.front_page_message'
        db.add_column(u'customizer_configuration', 'front_page_message',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Configuration.front_page_message'
        db.delete_column(u'customizer_configuration', 'front_page_message')


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
            'allow_admin_status_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_forum_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bibtex': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'chahub_data_hash': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'chahub_needs_retry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'chahub_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_on_submission_finished_successfully': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'method_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'method_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'newsletter_opt_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization_or_affiliation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'organizer_direct_message_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'organizer_status_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'participation_status_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'project_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'publication_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rabbitmq_password': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'rabbitmq_queue_limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5', 'blank': 'True'}),
            'rabbitmq_username': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'team_members': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'team_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'customizer.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'front_page_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'header_logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'only_competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Competition']", 'null': 'True', 'blank': 'True'})
        },
        u'queues.queue': {
            'Meta': {'object_name': 'Queue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'organizers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'organizers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['authenz.ClUser']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authenz.ClUser']"}),
            'vhost': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36', 'blank': 'True'})
        },
        u'teams.team': {
            'Meta': {'unique_together': "(('name', 'competition'),)", 'object_name': 'Team'},
            'allow_requests': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Competition']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_creator'", 'to': u"orm['authenz.ClUser']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_url_base': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'teams'", 'to': u"orm['authenz.ClUser']", 'through': u"orm['teams.TeamMembership']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teams.TeamStatus']", 'null': 'True'})
        },
        u'teams.teammembership': {
            'Meta': {'object_name': 'TeamMembership'},
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_invitation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teams.TeamMembershipStatus']", 'null': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_memberships'", 'to': u"orm['authenz.ClUser']"})
        },
        u'teams.teammembershipstatus': {
            'Meta': {'object_name': 'TeamMembershipStatus'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'teams.teamstatus': {
            'Meta': {'object_name': 'TeamStatus'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'web.competition': {
            'Meta': {'ordering': "['end_date']", 'object_name': 'Competition'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'competition_admins'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['authenz.ClUser']"}),
            'allow_organizer_teams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_public_submissions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_teams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'anonymous_leaderboard': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'chahub_data_hash': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'chahub_needs_retry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'chahub_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'competition_docker_image': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitioninfo_creator'", 'to': u"orm['authenz.ClUser']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'disallow_leaderboard_modifying': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_detailed_results': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_forum': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_medical_image_viewer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_per_submission_metadata': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_teams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'force_submission_to_leaderboard': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_registration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide_chart': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide_top_three': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_url_base': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'is_migrating': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_migrating_delayed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'last_phase_migration': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitioninfo_modified_by'", 'to': u"orm['authenz.ClUser']"}),
            'original_yaml_file': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'competitions'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['queues.Queue']"}),
            'require_team_approval': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reward': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'show_datasets_from_yaml': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'teams': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'competition_teams'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['teams.Team']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url_redirect': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['customizer']