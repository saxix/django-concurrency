# -*- coding: utf-8 -*-
from contextlib import contextmanager
import logging
from django.core.exceptions import ImproperlyConfigured
from concurrency.core import _select_lock, _wrap_model_save
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
    return not obj.__class__.objects.filter(**{obj._meta.pk.name: obj.pk,
                                               revision_field.attname: version}).exists()


def get_version(model_instance, version):
    version_field = model_instance.RevisionMetaInfo.field
    kwargs = {'pk': model_instance.pk, version_field.name: version}
    return model_instance.__class__.objects.get(**kwargs)


def get_object_with_version(manager, pk, version):
    version_field = manager.model.RevisionMetaInfo.field
    kwargs = {'pk': pk, version_field.name: version}
    return manager.get(**kwargs)


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

@contextmanager
def disable_sanity_check(model):
    old_value, model._revisionmetainfo.sanity_check = model._revisionmetainfo.sanity_check, False
    yield
    model._revisionmetainfo.sanity_check = old_value
