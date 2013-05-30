# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ImproperlyConfigured
from concurrency.core import _wrap_save, _select_lock, _wrap_model_save
from concurrency.exceptions import RecordModifiedError

__all__ = ['apply_concurrency_check', 'concurrency_check', 'get_revision_of_object', 'RecordModifiedError']

logger = logging.getLogger('concurrency')


def get_revision_of_object(obj):
    """

    @param obj:
    @return:
    """
    revision_field = obj.RevisionMetaInfo.field
    value = getattr(obj, revision_field.attname)
    return value


def is_changed(obj):
    revision_field = obj.RevisionMetaInfo.field
    version = getattr(obj, revision_field.attname)
    return not obj.__class__.objects.filter(**{obj._meta.pk.name:obj.pk,
                                           revision_field.attname: version}).exists()


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
    if hasattr(model, 'RevisionMetaInfo'):
        raise ImproperlyConfigured("%s is already under concurrency management" % model)

    logger.debug('Applying concurrency check to %s' % model)

    ver = versionclass()
    ver.contribute_to_class(model, fieldname)
    model.RevisionMetaInfo.field = ver

    if not model.RevisionMetaInfo.versioned_save:
        _wrap_model_save(model)


def concurrency_check(model_instance, force_insert=False, force_update=False, using=None, **kwargs):
    if not force_insert:
        _select_lock(model_instance)
