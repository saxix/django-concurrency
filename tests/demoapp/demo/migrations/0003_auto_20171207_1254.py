# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0002_auto_20160909_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conditionalversionmodelselfrelation',
            name='parent',
        ),
        migrations.AddField(
            model_name='conditionalversionmodelselfrelation',
            name='relations',
            field=models.ManyToManyField(to='demo.ConditionalVersionModelSelfRelation', null=True, through='demo.ThroughRelation', blank=True),
        ),
    ]
