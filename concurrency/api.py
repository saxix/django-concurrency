# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured

from django.utils.translation import gettext as _
from concurrency.core import _wrap_save, _select_lock

__all__ = ['apply_concurrency_check', 'concurrency_check']


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

    ver = versionclass()
    ver.contribute_to_class(model, fieldname)
    model.RevisionMetaInfo.field = ver

    if not model.RevisionMetaInfo.versioned_save:
        old_save = getattr(model, 'save')
        setattr(model, 'save', _wrap_save(old_save))
        model.RevisionMetaInfo.versioned_save = True


def concurrency_check(model_instance, force_insert=False, force_update=False, using=None, **kwargs):
    if not force_insert:
        _select_lock(model_instance)
