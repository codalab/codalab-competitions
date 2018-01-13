# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('competition', models.OneToOneField(related_name='forum', to='web.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField()),
                ('content', models.TextField()),
                ('posted_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField()),
                ('title', models.CharField(max_length=255)),
                ('last_post_date', models.DateTimeField(null=True, blank=True)),
                ('forum', models.ForeignKey(related_name='threads', to='forums.Forum')),
                ('started_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-last_post_date',),
            },
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(related_name='posts', to='forums.Thread'),
        ),
    ]
