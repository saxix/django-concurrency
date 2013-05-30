import logging
from functools import update_wrapper, wraps
from django.conf import settings
from django.db import connections, router
from django.utils.translation import ugettext as _

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger('concurrency').addHandler(NullHandler())

logger = logging.getLogger('concurrency')

from concurrency.exceptions import VersionChangedError, RecordModifiedError, InconsistencyError
from concurrency.utils import deprecated


__all__ = []


@deprecated('concurrency.api.apply_concurrency_check', '0.5')
def apply_concurrency_check(model, fieldname, versionclass):
    from concurrency.api import apply_concurrency_check as acc
    return acc(model, fieldname, versionclass)


@deprecated('concurrency.api.concurrency_check', '0.5')
def concurrency_check(model_instance, force_insert=False, force_update=False, using=None, **kwargs):
    from concurrency.api import concurrency_check as cc
    return cc(model_instance, force_insert, force_update, using, **kwargs)


def _select_lock(model_instance, version_value=None):
    version_field = model_instance.RevisionMetaInfo.field
    value = version_value or getattr(model_instance, version_field.name)
    is_versioned = value != version_field.get_default()
    if model_instance.pk is not None:
        kwargs = {'pk': model_instance.pk, version_field.name: value}
        alias = router.db_for_write(model_instance)
        NOWAIT = connections[alias].features.has_select_for_update_nowait
        entry = model_instance.__class__.objects.select_for_update(nowait=NOWAIT).filter(**kwargs)
        if not entry:
            raise RecordModifiedError(_('Record has been modified'), target=model_instance)
    elif is_versioned and getattr(settings, 'CONCURRECY_SANITY_CHECK', True):
        raise InconsistencyError(_('Version field is set (%s) but record has not `pk`.' % value))


def _wrap_model_save(model, force=False):
    if force or not model.RevisionMetaInfo.versioned_save:
        logger.debug('Wrapping save method of %s' % model)
        old_save = getattr(model, 'save')
        setattr(model, 'save', _wrap_save(old_save))
        model.RevisionMetaInfo.versioned_save = True


def _wrap_save(func):
    from concurrency.api import  concurrency_check
    def inner(self, force_insert=False, force_update=False, using=None, **kwargs):
        concurrency_check(self, force_insert, force_update, using, **kwargs)
        return func(self, force_insert, force_update, using, **kwargs)

    return update_wrapper(inner, func)


def _versioned_save(self, force_insert=False, force_update=False, using=None):
    if force_insert and force_update:
        raise ValueError("Cannot force both insert and updating in model saving.")
    if not force_insert:
        _select_lock(self)
    self.save_base(using=using, force_insert=force_insert, force_update=force_update)


class RevisionMetaInfo:
    field = None
    versioned_save = False
    manually = False

