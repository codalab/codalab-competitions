# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'NewsletterUser.user'
        db.delete_column(u'newsletter_newsletteruser', 'user_id')


    def backwards(self, orm):
        # Adding field 'NewsletterUser.user'
        db.add_column(u'newsletter_newsletteruser', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['authenz.ClUser'], null=True, blank=True),
                      keep_default=False)


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