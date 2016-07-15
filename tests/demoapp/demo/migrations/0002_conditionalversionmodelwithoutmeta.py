# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models

import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('demo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConditionalVersionModelWithoutMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('version', concurrency.fields.ConditionalVersionField(default=1, help_text='record revision number')),
                ('field1', models.CharField(unique=True, blank=True, max_length=30, null=True)),
                ('field2', models.CharField(unique=True, blank=True, max_length=30, null=True)),
                ('field3', models.CharField(unique=True, blank=True, max_length=30, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
