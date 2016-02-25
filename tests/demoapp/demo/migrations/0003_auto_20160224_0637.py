# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0002_conditionalversionmodelwithoutmeta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anything',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=10)),
                ('a_relation', models.ForeignKey(to='demo.ConditionalVersionModelWithoutMeta')),
            ],
        ),
        migrations.AddField(
            model_name='conditionalversionmodelwithoutmeta',
            name='anythings',
            field=models.ManyToManyField(to='demo.Anything'),
        ),
    ]
