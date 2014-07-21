# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='version',
            field=concurrency.fields.IntegerVersionField(help_text='record revision number', default=1),
            preserve_default=True,
        ),
    ]
