# -*- coding: utf-8 -*-
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    depends_on = (
        ("authenz", "0002_auto__add_cluser"),
    )

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass

    models = {

    }

    complete_apps = ['web']
