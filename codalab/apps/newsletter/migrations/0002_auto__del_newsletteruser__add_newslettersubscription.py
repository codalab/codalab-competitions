# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'NewsletterUser'
        db.delete_table(u'newsletter_newsletteruser')

        # Adding model 'NewsletterSubscription'
        db.create_table(u'newsletter_newslettersubscription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('subscription_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('needs_retry', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'newsletter', ['NewsletterSubscription'])


    def backwards(self, orm):
        # Adding model 'NewsletterUser'
        db.create_table(u'newsletter_newsletteruser', (
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(default=None, max_length=75, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'newsletter', ['NewsletterUser'])

        # Deleting model 'NewsletterSubscription'
        db.delete_table(u'newsletter_newslettersubscription')


    models = {
        u'newsletter.newslettersubscription': {
            'Meta': {'object_name': 'NewsletterSubscription'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'needs_retry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subscription_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['newsletter']