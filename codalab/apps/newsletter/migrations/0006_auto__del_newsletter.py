# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Newsletter'
        db.delete_table(u'newsletter_newsletter')

        # Removing M2M table for field email on 'Newsletter'
        db.delete_table(db.shorten_name(u'newsletter_newsletter_email'))


    def backwards(self, orm):
        # Adding model 'Newsletter'
        db.create_table(u'newsletter_newsletter', (
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=250)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'newsletter', ['Newsletter'])

        # Adding M2M table for field email on 'Newsletter'
        m2m_table_name = db.shorten_name(u'newsletter_newsletter_email')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newsletter', models.ForeignKey(orm[u'newsletter.newsletter'], null=False)),
            ('newsletteruser', models.ForeignKey(orm[u'newsletter.newsletteruser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['newsletter_id', 'newsletteruser_id'])


    models = {
        u'newsletter.newsletteruser': {
            'Meta': {'object_name': 'NewsletterUser'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['newsletter']