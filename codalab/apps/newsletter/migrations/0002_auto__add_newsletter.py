# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Newsletter'
        db.create_table(u'newsletter_newsletter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
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


    def backwards(self, orm):
        # Deleting model 'Newsletter'
        db.delete_table(u'newsletter_newsletter')

        # Removing M2M table for field email on 'Newsletter'
        db.delete_table(db.shorten_name(u'newsletter_newsletter_email'))


    models = {
        u'newsletter.newsletter': {
            'Meta': {'object_name': 'Newsletter'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['newsletter.NewsletterUser']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'newsletter.newsletteruser': {
            'Meta': {'object_name': 'NewsletterUser'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['newsletter']