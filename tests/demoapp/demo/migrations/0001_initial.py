# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoIncConcurrentModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('version', concurrency.fields.AutoIncVersionField(default=0, db_column='cm_version_id', help_text='record revision number')),
                ('username', models.CharField(max_length=30, blank=True, null=True)),
                ('date_field', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'AutoIncConcurrentModel',
                'verbose_name': 'AutoIncConcurrentModel',
            },
        ),
        migrations.CreateModel(
            name='ConcreteModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('version', concurrency.fields.IntegerVersionField(default=0, db_column='cm_version_id', help_text='record revision number')),
                ('username', models.CharField(max_length=30, unique=True, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupTestModel',
            fields=[
                ('group_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='auth.Group')),
                ('username', models.CharField(max_length=50, verbose_name='username')),
            ],
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='Issue3TestModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('username', models.CharField(max_length=30, blank=True, null=True)),
                ('last_name', models.CharField(max_length=30, blank=True, null=True)),
                ('char_field', models.CharField(max_length=30, blank=True, null=True)),
                ('date_field', models.DateField(blank=True, null=True)),
                ('version', models.CharField(max_length=10, default='abc', blank=True, null=True)),
                ('revision', concurrency.fields.IntegerVersionField(default=0, db_column='cm_version_id', help_text='record revision number')),
            ],
        ),
        migrations.CreateModel(
            name='ReversionConcurrentModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('version', concurrency.fields.IntegerVersionField(default=0, db_column='cm_version_id', help_text='record revision number')),
                ('username', models.CharField(max_length=30, unique=True, blank=True, null=True)),
                ('date_field', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Reversion-ConcurrentModels',
                'verbose_name': 'Reversion-ConcurrentModel',
            },
        ),
        migrations.CreateModel(
            name='SimpleConcurrentModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('version', concurrency.fields.IntegerVersionField(default=0, db_column='cm_version_id', help_text='record revision number')),
                ('username', models.CharField(max_length=30, unique=True, blank=True, null=True)),
                ('date_field', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'SimpleConcurrentModels',
                'verbose_name': 'SimpleConcurrentModel',
            },
        ),
        migrations.CreateModel(
            name='TriggerConcurrentModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('version', concurrency.fields.TriggerVersionField(default=0, db_column='cm_version_id', help_text='record revision number')),
                ('username', models.CharField(max_length=30, blank=True, null=True)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'TriggerConcurrentModels',
                'verbose_name': 'TriggerConcurrentModel',
            },
        ),
        migrations.CreateModel(
            name='DropTriggerConcurrentModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('version', concurrency.fields.TriggerVersionField(default=0, db_column='cm_version_id', help_text='record revision number')),
                ('username', models.CharField(max_length=30, blank=True, null=True)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'TriggerConcurrentModels',
                'verbose_name': 'TriggerConcurrentModel',
            },
        ),
        migrations.CreateModel(
            name='ConcurrencyDisabledModel',
            fields=[
                ('simpleconcurrentmodel_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='demo.SimpleConcurrentModel')),
                ('dummy_char', models.CharField(max_length=30, blank=True, null=True)),
            ],
            bases=('demo.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='CustomSaveModel',
            fields=[
                ('simpleconcurrentmodel_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='demo.SimpleConcurrentModel')),
                ('extra_field', models.CharField(max_length=30, unique=True, blank=True, null=True)),
            ],
            bases=('demo.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='InheritedModel',
            fields=[
                ('simpleconcurrentmodel_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='demo.SimpleConcurrentModel')),
                ('extra_field', models.CharField(max_length=30, unique=True, blank=True, null=True)),
            ],
            bases=('demo.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='ListEditableConcurrentModel',
            fields=[
            ],
            options={
                'verbose_name_plural': 'ListEditableConcurrentModels',
                'verbose_name': 'ListEditableConcurrentModel',
                'proxy': True,
            },
            bases=('demo.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='NoActionsConcurrentModel',
            fields=[
            ],
            options={
                'verbose_name_plural': 'NoActions-ConcurrentModels',
                'verbose_name': 'NoActions-ConcurrentModel',
                'proxy': True,
            },
            bases=('demo.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='ProxyModel',
            fields=[
            ],
            options={
                'verbose_name_plural': 'ProxyModels',
                'verbose_name': 'ProxyModel',
                'proxy': True,
            },
            bases=('demo.simpleconcurrentmodel',),
        ),
    ]
