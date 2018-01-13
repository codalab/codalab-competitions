# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Date of creation')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name=b'Date of last update')),
                ('status', models.PositiveIntegerField(default=0, verbose_name=b'Status', db_index=True)),
                ('task_type', models.CharField(max_length=256, verbose_name=b'Task type')),
                ('task_args_json', models.TextField(verbose_name=b'JSON-encoded task arguments', blank=True)),
                ('task_info_json', models.TextField(verbose_name=b'JSON-encoded task information', blank=True)),
            ],
        ),
    ]
