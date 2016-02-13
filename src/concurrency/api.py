# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from django.db.models import Model

from concurrency.config import conf
from concurrency.core import _select_lock, get_version_fieldname  # _wrap_model_save
from concurrency.exceptions import RecordModifiedError

__all__ = ['apply_concurrency_check', 'concurrency_check', 'get_revision_of_object',
           'RecordModifiedError', 'disable_concurrency',
           'get_version', 'is_changed', 'get_version_fieldname']

logger = logging.getLogger(__name__)


def get_revision_of_object(obj):
    """
        returns teh version of the passed object

    @param obj:
    @return:
    """
    return getattr(obj, get_version_fieldname(obj))


def is_changed(obj):
    """
        returns True if `obj` is changed or deleted on the database
    :param obj:
    :return:
    """
    revision_field = get_version_fieldname(obj)
    version = get_revision_of_object(obj)
    return not obj.__class__.objects.filter(**{obj._meta.pk.name: obj.pk,
                                               revision_field: version}).exists()


def get_version(model_instance, version):
    """
        try go load from the database one object with specific version

    :param model_instance: instance in memory
    :param version: version number
    :return:
    """
    version_field = get_version_fieldname(model_instance)
    kwargs = {'pk': model_instance.pk, version_field: version}
    return model_instance.__class__.objects.get(**kwargs)


def apply_concurrency_check(model, fieldname, versionclass):
    if hasattr(model, '_concurrencymeta'):
        return

    logger.debug('Applying concurrency check to %s' % model)

    ver = versionclass()

    ver.contribute_to_class(model, fieldname)
    model._concurrencymeta.field = ver

    from concurrency.fields import class_prepared_concurrency_handler

    class_prepared_concurrency_handler(model)

    if not model._concurrencymeta.versioned_save:
        versionclass._wrap_model_save(model)


def concurrency_check(model_instance, force_insert=False, force_update=False, using=None, **kwargs):
    if not force_insert:
        _select_lock(model_instance)


class concurrency_disable_increment(object):
    def __init__(self, model):
        self.model = model
        self.old_value = model._concurrencymeta.increment

    def __enter__(self):
        if isinstance(self.model, Model):
            self.old_value, self.model._concurrency_disable_increment = getattr(self.model, '_concurrency_disable_increment', False), True
            self.model._concurrency_disabled = True
        else:
            self.old_value, self.model._concurrencymeta.increment = self.model._concurrencymeta.increment, False

    def __exit__(self, *args, **kwds):
        if isinstance(self.model, Model):
            self.model._concurrency_disable_increment = self.old_value
        else:
            self.model._concurrencymeta.increment = self.old_value

    def __call__(self, func):
        def wrapper(*args, **kwds):
            with self:
                return func(*args, **kwds)

        return wrapper


class disable_concurrency(object):
    """
        temporary disable concurrency

    can be used either as contextmanager or decorator.
    It can applied to model instances, model class of globally.

    :param model: model instance, model class or None
    """

    def __init__(self, model=None):
        self.model = model
        self.old_value = conf.ENABLED
        self.concurrency_managed = (model is None) or hasattr(model, '_concurrencymeta')

    def __enter__(self):
        if not self.concurrency_managed:
            return
        if self.model is None:
            self.old_value, conf.ENABLED = conf.ENABLED, False
        elif isinstance(self.model, Model):
            self.old_value, self.model._concurrency_disabled = getattr(self.model, '_concurrency_disabled', False), True
            self.model._concurrency_disabled = True
        else:
            self.old_value, self.model._concurrencymeta.enabled = self.model._concurrencymeta.enabled, False

    def __exit__(self, *args, **kwds):
        if not self.concurrency_managed:
            return
        if self.model is None:
            conf.ENABLED = self.old_value
        elif isinstance(self.model, Model):
            self.model._concurrency_disabled = self.old_value
        else:
            self.model._concurrencymeta.enabled = self.old_value

    def __call__(self, func):
        def wrapper(*args, **kwds):
            with self:
                return func(*args, **kwds)

        return wrapper
