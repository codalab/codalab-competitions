# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'HealthSettings.congestion_threshold'
        db.alter_column(u'health_healthsettings', 'congestion_threshold', self.gf('django.db.models.fields.PositiveIntegerField')())

    def backwards(self, orm):

        # Changing field 'HealthSettings.congestion_threshold'
        db.alter_column(u'health_healthsettings', 'congestion_threshold', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

    models = {
        u'health.healthsettings': {
            'Meta': {'object_name': 'HealthSettings'},
            'congestion_threshold': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'emails': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'threshold': ('django.db.models.fields.PositiveIntegerField', [], {'default': '25', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['health']