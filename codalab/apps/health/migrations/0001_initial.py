# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HealthSettings'
        db.create_table(u'health_healthsettings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('emails', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'health', ['HealthSettings'])


    def backwards(self, orm):
        # Deleting model 'HealthSettings'
        db.delete_table(u'health_healthsettings')


    models = {
        u'health.healthsettings': {
            'Meta': {'object_name': 'HealthSettings'},
            'emails': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['health']