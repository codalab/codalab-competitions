# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'HealthSettings.emails'
        db.alter_column(u'health_healthsettings', 'emails', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'HealthSettings.emails'
        db.alter_column(u'health_healthsettings', 'emails', self.gf('django.db.models.fields.TextField')(default=''))

    models = {
        u'health.healthsettings': {
            'Meta': {'object_name': 'HealthSettings'},
            'emails': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['health']