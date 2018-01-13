# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HealthSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('emails', models.TextField(null=True, blank=True)),
                ('threshold', models.PositiveIntegerField(default=25, null=True, blank=True)),
            ],
        ),
    ]
