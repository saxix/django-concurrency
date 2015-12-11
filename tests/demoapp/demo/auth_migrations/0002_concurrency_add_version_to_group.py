# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

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
            model_name='Group',
            name='version',
            field=IntegerVersionField(help_text=b'Version', default=1),

        ),
    ]
