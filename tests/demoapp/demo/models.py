# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import Group, User
from django.db import models

from concurrency.fields import (
    AutoIncVersionField, ConditionalVersionField, IntegerVersionField,
    TriggerVersionField
)

__all__ = ['SimpleConcurrentModel', 'AutoIncConcurrentModel',
           'ProxyModel', 'InheritedModel', 'CustomSaveModel',
           'ConcreteModel', 'TriggerConcurrentModel',
           'ConditionalVersionModelWithoutMeta',
           'Anything',
           ]


class SimpleConcurrentModel(models.Model):
    version = IntegerVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True, unique=True)
    date_field = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'demo'
        verbose_name = "SimpleConcurrentModel"
        verbose_name_plural = "SimpleConcurrentModels"

    def __str__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.pk)

    def __unicode__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.pk)


class AutoIncConcurrentModel(models.Model):
    version = AutoIncVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'demo'
        verbose_name = "AutoIncConcurrentModel"
        verbose_name_plural = "AutoIncConcurrentModel"

    def __unicode__(self):
        return "{0.__class__.__name__} #{0.pk}".format(self)


class TriggerConcurrentModel(models.Model):
    version = TriggerVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True)
    count = models.IntegerField(default=0)

    class Meta:
        app_label = 'demo'
        verbose_name = "TriggerConcurrentModel"
        verbose_name_plural = "TriggerConcurrentModels"

    def __unicode__(self):
        return "{0.__class__.__name__} #{0.pk}".format(self)


class DropTriggerConcurrentModel(models.Model):
    # only used to test drop triggers
    version = TriggerVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True)
    count = models.IntegerField(default=0)

    class Meta:
        app_label = 'demo'


class ProxyModel(SimpleConcurrentModel):
    class Meta:
        app_label = 'demo'
        proxy = True
        verbose_name = "ProxyModel"
        verbose_name_plural = "ProxyModels"


class InheritedModel(SimpleConcurrentModel):
    extra_field = models.CharField(max_length=30, blank=True, null=True, unique=True)

    class Meta:
        app_label = 'demo'


class CustomSaveModel(SimpleConcurrentModel):
    extra_field = models.CharField(max_length=30, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        super(CustomSaveModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'demo'


class AbstractModel(models.Model):
    version = IntegerVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True, unique=True)

    class Meta:
        app_label = 'demo'
        abstract = True


class ConcreteModel(AbstractModel):
    pass

    class Meta:
        app_label = 'demo'


# class TestCustomUser(User):
# version = IntegerVersionField(db_column='cm_version_id')
#
#     class Meta:
#         app_label = 'demo'
#
#     def __unicode__(self):
#         return "{0.__class__.__name__} #{0.pk}".format(self)


class GroupTestModel(Group):
    # HACK: this field is here because all tests relies on that
    # and we need a 'fresh' model to check for on-the-fly addition
    # of version field.  (added in tests 0.3.0)

    username = models.CharField('username', max_length=50)

    class Meta:
        app_label = 'demo'


# class TestModelGroupWithCustomSave(TestModelGroup):
#     class Meta:
#         app_label = 'demo'
#
#     def save(self, *args, **kwargs):
#         super(TestModelGroupWithCustomSave, self).save(*args, **kwargs)
#         return 222


class Issue3TestModel(models.Model):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    char_field = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)

    version = models.CharField(default='abc', max_length=10, blank=True, null=True)
    revision = IntegerVersionField(db_column='cm_version_id')

    class Meta:
        app_label = 'demo'


class ListEditableConcurrentModel(SimpleConcurrentModel):
    """ Proxy model used by admin related test.
    This allow to use multiple ModelAdmin configuration with the same 'real' model
    """

    class Meta:
        app_label = 'demo'
        proxy = True
        verbose_name = "ListEditableConcurrentModel"
        verbose_name_plural = "ListEditableConcurrentModels"


class NoActionsConcurrentModel(SimpleConcurrentModel):
    """ Proxy model used by admin related test.
    This allow to use multiple ModelAdmin configuration with the same 'real' model
    """

    class Meta:
        app_label = 'demo'
        proxy = True
        verbose_name = "NoActions-ConcurrentModel"
        verbose_name_plural = "NoActions-ConcurrentModels"


class ReversionConcurrentModel(models.Model):
    version = IntegerVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True, unique=True)
    date_field = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'demo'
        verbose_name = "Reversion-ConcurrentModel"
        verbose_name_plural = "Reversion-ConcurrentModels"

    def __unicode__(self):
        return "{0.__class__.__name__} #{0.pk}".format(self)


class ConcurrencyDisabledModel(SimpleConcurrentModel):
    dummy_char = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        app_label = 'demo'

    class ConcurrencyMeta:
        enabled = False


class ConditionalVersionModel(models.Model):
    version = ConditionalVersionField()
    field1 = models.CharField(max_length=30, blank=True, null=True, unique=True)
    field2 = models.CharField(max_length=30, blank=True, null=True, unique=True)
    field3 = models.CharField(max_length=30, blank=True, null=True, unique=True)
    user = models.ForeignKey(User, null=True)

    class Meta:
        app_label = 'demo'

    class ConcurrencyMeta:
        check_fields = ['field1', 'field2', 'user']


class Anything(models.Model):
    """
    Will create a ManyToOneRel automatic field on
    ConditionalVersionModelWithoutMeta instances.
    """
    name = models.CharField(max_length=10)
    a_relation = models.ForeignKey('demo.ConditionalVersionModelWithoutMeta')


class ConditionalVersionModelWithoutMeta(models.Model):
    """
    This model doesn't have ConcurrencyMeta defined.
    """
    version = ConditionalVersionField()
    field1 = models.CharField(max_length=30, blank=True, null=True, unique=True)
    field2 = models.CharField(max_length=30, blank=True, null=True, unique=True)
    field3 = models.CharField(max_length=30, blank=True, null=True, unique=True)
    user = models.ForeignKey(User, null=True)
    anythings = models.ManyToManyField(Anything)

    class Meta:
        app_label = 'demo'
