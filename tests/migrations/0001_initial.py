# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import concurrency.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoIncConcurrentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('version', concurrency.fields.AutoIncVersionField(help_text='record revision number', db_column=b'cm_version_id', default=1)),
                ('username', models.CharField(blank=True, null=True, max_length=30)),
                ('date_field', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': b'AutoIncConcurrentModel',
                'verbose_name_plural': b'AutoIncConcurrentModel',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConcreteModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('version', concurrency.fields.IntegerVersionField(help_text='record revision number', db_column=b'cm_version_id', default=1)),
                ('username', models.CharField(blank=True, null=True, max_length=30, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleConcurrentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('version', concurrency.fields.IntegerVersionField(help_text='record revision number', db_column=b'cm_version_id', default=1)),
                ('username', models.CharField(blank=True, null=True, max_length=30, unique=True)),
                ('date_field', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': b'SimpleConcurrentModel',
                'verbose_name_plural': b'SimpleConcurrentModels',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InheritedModel',
            fields=[
                ('simpleconcurrentmodel_ptr', models.OneToOneField(auto_created=True, to='tests.SimpleConcurrentModel', primary_key=True, serialize=False)),
                ('extra_field', models.CharField(blank=True, null=True, max_length=30, unique=True)),
            ],
            options={
            },
            bases=('tests.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='CustomSaveModel',
            fields=[
                ('simpleconcurrentmodel_ptr', models.OneToOneField(auto_created=True, to='tests.SimpleConcurrentModel', primary_key=True, serialize=False)),
                ('extra_field', models.CharField(blank=True, null=True, max_length=30, unique=True)),
            ],
            options={
            },
            bases=('tests.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='ConcurrencyDisabledModel',
            fields=[
                ('simpleconcurrentmodel_ptr', models.OneToOneField(auto_created=True, to='tests.SimpleConcurrentModel', primary_key=True, serialize=False)),
                ('dummy_char', models.CharField(blank=True, null=True, max_length=30)),
            ],
            options={
            },
            bases=('tests.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='TestIssue3Model',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('username', models.CharField(blank=True, null=True, max_length=30)),
                ('last_name', models.CharField(blank=True, null=True, max_length=30)),
                ('char_field', models.CharField(blank=True, null=True, max_length=30)),
                ('date_field', models.DateField(blank=True, null=True)),
                ('version', models.CharField(blank=True, null=True, max_length=10, default=b'abc')),
                ('revision', concurrency.fields.IntegerVersionField(help_text='record revision number', db_column=b'cm_version_id', default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestModelGroup',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, to='auth.Group', primary_key=True, serialize=False)),
                ('username', models.CharField(verbose_name=b'username', max_length=50)),
            ],
            options={
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='TriggerConcurrentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('version', concurrency.fields.TriggerVersionField(help_text='record revision number', db_column=b'cm_version_id', default=1)),
                ('username', models.CharField(blank=True, null=True, max_length=30)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': b'TriggerConcurrentModel',
                'verbose_name_plural': b'TriggerConcurrentModels',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ListEditableConcurrentModel',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': b'ListEditableConcurrentModel',
                'verbose_name_plural': b'ListEditableConcurrentModels',
            },
            bases=('tests.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='NoActionsConcurrentModel',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': b'NoActions-ConcurrentModel',
                'verbose_name_plural': b'NoActions-ConcurrentModels',
            },
            bases=('tests.simpleconcurrentmodel',),
        ),
        migrations.CreateModel(
            name='ProxyModel',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': b'ProxyModel',
                'verbose_name_plural': b'ProxyModels',
            },
            bases=('tests.simpleconcurrentmodel',),
        ),


    ]
