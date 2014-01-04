# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.db import models
from concurrency.fields import IntegerVersionField, AutoIncVersionField, TriggerVersionField

__all__ = ['SimpleConcurrentModel', 'AutoIncConcurrentModel',
           'ProxyModel', 'InheritedModel', 'CustomSaveModel',
           'ConcreteModel']


class SimpleConcurrentModel(models.Model):
    version = IntegerVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True, unique=True)
    date_field = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'concurrency'
        verbose_name = "SimpleConcurrentModel"
        verbose_name_plural = "SimpleConcurrentModels"

    def __unicode__(self):
        return "{0.__class__.__name__} #{0.pk}".format(self)


class AutoIncConcurrentModel(models.Model):
    version = AutoIncVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'concurrency'
        verbose_name = "AutoIncConcurrentModel"
        verbose_name_plural = "AutoIncConcurrentModel"

    def __unicode__(self):
        return "{0.__class__.__name__} #{0.pk}".format(self)


class TriggerConcurrentModel(models.Model):
    version = TriggerVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True)
    count = models.IntegerField(default=0)

    class Meta:
        app_label = 'concurrency'
        verbose_name = "TriggerConcurrentModel"
        verbose_name_plural = "TriggerConcurrentModels"

    def __unicode__(self):
        return "{0.__class__.__name__} #{0.pk}".format(self)


class ProxyModel(SimpleConcurrentModel):
    class Meta:
        app_label = 'concurrency'
        proxy = True
        verbose_name = "ProxyModel"
        verbose_name_plural = "ProxyModels"


class InheritedModel(SimpleConcurrentModel):
    extra_field = models.CharField(max_length=30, blank=True, null=True, unique=True)

    class Meta:
        app_label = 'concurrency'


class CustomSaveModel(SimpleConcurrentModel):
    extra_field = models.CharField(max_length=30, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        super(CustomSaveModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'concurrency'


class AbstractModel(models.Model):
    version = IntegerVersionField(db_column='cm_version_id')
    username = models.CharField(max_length=30, blank=True, null=True, unique=True)

    class Meta:
        app_label = 'concurrency'
        abstract = True


class ConcreteModel(AbstractModel):
    pass

    class Meta:
        app_label = 'concurrency'

# class TestCustomUser(User):
#     version = IntegerVersionField(db_column='cm_version_id')
#
#     class Meta:
#         app_label = 'concurrency'
#
#     def __unicode__(self):
#         return "{0.__class__.__name__} #{0.pk}".format(self)


class TestModelGroup(Group):
    #HACK: this field is here because all tests relies on that
    # and we need a 'fresh' model to check for on-the-fly addition
    # of version field.  (added in concurrency 0.3.0)

    username = models.CharField('username', max_length=50)

    class Meta:
        app_label = 'concurrency'


# class TestModelGroupWithCustomSave(TestModelGroup):
#     class Meta:
#         app_label = 'concurrency'
#
#     def save(self, *args, **kwargs):
#         super(TestModelGroupWithCustomSave, self).save(*args, **kwargs)
#         return 222


class TestIssue3Model(models.Model):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    char_field = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)

    version = models.CharField(default='abc', max_length=10, blank=True, null=True)
    revision = IntegerVersionField(db_column='cm_version_id')

    class Meta:
        app_label = 'concurrency'


class ListEditableConcurrentModel(SimpleConcurrentModel):
    """ Proxy model used by admin related test.
    This allow to use multiple ModelAdmin configuration with the same 'real' model
    """

    class Meta:
        app_label = 'concurrency'
        proxy = True
        verbose_name = "ListEditableConcurrentModel"
        verbose_name_plural = "ListEditableConcurrentModels"


class NoActionsConcurrentModel(SimpleConcurrentModel):
    """ Proxy model used by admin related test.
    This allow to use multiple ModelAdmin configuration with the same 'real' model
    """

    class Meta:
        app_label = 'concurrency'
        proxy = True
        verbose_name = "NoActions-ConcurrentModel"
        verbose_name_plural = "NoActions-ConcurrentModels"


class ConcurrencyDisabledModel(SimpleConcurrentModel):
    dummy_char = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        app_label = 'concurrency'

    class ConcurrencyMeta:
        enabled = False
