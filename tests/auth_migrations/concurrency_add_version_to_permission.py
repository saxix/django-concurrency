# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import validators
from django.db import models, migrations
from django.utils import timezone
from concurrency.fields import IntegerVersionField


class Migration(migrations.Migration):
    """
    To enabe this migration you must add this code to your settings

        MIGRATION_MODULES = {
            ...
            ...
            'auth': 'tests.auth_migrations',
        }

    """
    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='Permission',
            name='version',
            field=IntegerVersionField(),

        )]
