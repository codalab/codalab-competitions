# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import storages.backends.gcloud


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('image', models.FileField(storage=storages.backends.gcloud.GoogleCloudStorage(bucket_name=b'codalab-test'), upload_to=b'team_logo', null=True, verbose_name=b'Logo', blank=True)),
                ('image_url_base', models.CharField(max_length=255)),
                ('allow_requests', models.BooleanField(default=True, verbose_name=b'Allow requests')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=100, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_invitation', models.BooleanField(default=False)),
                ('is_request', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField(null=True, verbose_name=b'Start Date (UTC)', blank=True)),
                ('end_date', models.DateTimeField(null=True, verbose_name=b'End Date (UTC)', blank=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('reason', models.CharField(max_length=100, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeamMembershipStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('codename', models.CharField(unique=True, max_length=30)),
                ('description', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TeamStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('codename', models.CharField(unique=True, max_length=30)),
                ('description', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='teammembership',
            name='status',
            field=models.ForeignKey(to='teams.TeamMembershipStatus', null=True),
        ),
        migrations.AddField(
            model_name='teammembership',
            name='team',
            field=models.ForeignKey(to='teams.Team'),
        ),
        migrations.AddField(
            model_name='teammembership',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
