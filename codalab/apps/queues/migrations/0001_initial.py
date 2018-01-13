# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('vhost', django_extensions.db.fields.UUIDField(unique=True, editable=False, blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('organizers', models.ManyToManyField(help_text=b'(Organizers allowed to view this queue when they assign their competition to a queue)', related_name='organizers', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
