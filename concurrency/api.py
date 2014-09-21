# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from inspect import isclass
import logging
from contextlib import contextmanager
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from concurrency.core import _select_lock, _wrap_model_save, get_version_fieldname
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


# def get_object_with_version(manager, pk, version):
#     """
#         try go load from the database one object with specific version.
#         Raises DoesNotExists otherwise.
#
#     :param manager: django.models.Manager
#     :param pk: primaryKey
#     :param version: version number
#     :return:
#     """
#     version_field = manager.model._concurrencymeta._field
#     kwargs = {'pk': pk, version_field.name: version}
#     return manager.get(**kwargs)


def apply_concurrency_check(model, fieldname, versionclass):
    """
    Apply concurrency management to existing Models.

    :param model: Model class to update
    :type model: django.db.Model

    :param fieldname: name of the field
    :type fieldname: basestring

    :param versionclass:
    :type versionclass: concurrency.fields.VersionField subclass
    """
    if hasattr(model, '_concurrencymeta'):
        return

    logger.debug('Applying concurrency check to %s' % model)

    ver = versionclass()

    ver.contribute_to_class(model, fieldname)
    model._concurrencymeta._field = ver

    from concurrency.fields import class_prepared_concurrency_handler
    class_prepared_concurrency_handler(model)

    if not model._concurrencymeta._versioned_save:
        _wrap_model_save(model)


def concurrency_check(model_instance, force_insert=False, force_update=False, using=None, **kwargs):
    if not force_insert:
        _select_lock(model_instance)


@contextmanager
def disable_concurrency(model):
    """
        temporary disable concurrency check for passed model
    :param model:
    """
    if isinstance(model, Model):
        old_value, model._concurrency_disabled = getattr(model, '_concurrency_disabled', False), True
        model._concurrency_disabled = True
    else:
        old_value, model._concurrencymeta.enabled = model._concurrencymeta.enabled, False
    yield
    if isinstance(model, Model):
        model._concurrency_disabled  = old_value
    else:
        model._concurrencymeta.enabled = old_value
