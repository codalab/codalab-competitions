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
            name='Dislike',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('submission', models.ForeignKey(related_name='dislikes', to='web.CompetitionSubmission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DownloadRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('submission', models.ForeignKey(related_name='downloads', to='web.CompetitionSubmission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('submission', models.ForeignKey(related_name='likes', to='web.CompetitionSubmission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set([('submission', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='downloadrecord',
            unique_together=set([('submission', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='dislike',
            unique_together=set([('submission', 'user')]),
        ),
    ]
