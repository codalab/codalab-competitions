# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('header_logo', models.ImageField(null=True, upload_to=b'main_logo', blank=True)),
                ('only_competition', models.ForeignKey(blank=True, to='web.Competition', null=True)),
            ],
        ),
    ]
