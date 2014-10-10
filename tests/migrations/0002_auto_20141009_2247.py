# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name = 'TestIssue41Modal',
            fields = [
                ('id', models.AutoField(verbose_name = 'ID', serialize = False, auto_created = True, primary_key = True)),
                ('version', concurrency.fields.TriggerVersionField(default = 0, help_text = 'record revision number')),
            ],
            options = {
                'db_table': 'issue41',
            },
            bases = (models.Model,),
        )
    ]
