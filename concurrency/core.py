from __future__ import absolute_import
import logging
from functools import update_wrapper
from django.db import connections, router
from django.utils.translation import ugettext as _
from concurrency.config import conf, CONCURRENCY_POLICY_CALLBACK
from concurrency.exceptions import RecordModifiedError

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger('concurrency').addHandler(NullHandler())

logger = logging.getLogger(__name__)

__all__ = []


def get_version_fieldname(obj):
    return obj._concurrencymeta._field.attname


def _set_version(obj, version):
    """
    Set the given version on the passed object

    This function should be used with 'raw' values, any type conversion should be managed in
    VersionField._set_version_value(). This is needed for future enhancement of concurrency.
    """
    obj._concurrencymeta._field._set_version_value(obj, version)


def _select_lock(model_instance, version_value=None):
    if not conf.ENABLED:
        return
    version_field = model_instance._concurrencymeta._field
    value = version_value or getattr(model_instance, version_field.name)
    is_versioned = value != version_field.get_default()
    if model_instance.pk is not None and is_versioned:
        kwargs = {'pk': model_instance.pk, version_field.name: value}
        alias = router.db_for_write(model_instance)
        NOWAIT = connections[alias].features.has_select_for_update_nowait
        entry = model_instance.__class__._base_manager.select_for_update(nowait=NOWAIT).filter(**kwargs)
        if not entry:
            logger.debug("Conflict detected on `{0}` pk:`{0.pk}`, "
                         "version `{1}` not found".format(model_instance, value))
            conf._callback(model_instance)

def _wrap_model_save(model, force=False):
    if force or not model._concurrencymeta._versioned_save:
        logger.debug('Wrapping save method of %s' % model)
        old_save = getattr(model, 'save')
        setattr(model, 'save', _wrap_save(old_save))
        from concurrency.api import get_version

        setattr(model, 'get_concurrency_version', get_version)

        model._concurrencymeta._versioned_save = True


def _wrap_save(func):
    from concurrency.api import concurrency_check

    def inner(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self._concurrencymeta.enabled:
            concurrency_check(self, force_insert, force_update, using, **kwargs)
        return func(self, force_insert, force_update, using, **kwargs)

    return update_wrapper(inner, func)


class ConcurrencyOptions:
    _field = None
    _versioned_save = False
    _manually = False
    enabled = True
