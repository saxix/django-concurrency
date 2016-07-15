from __future__ import absolute_import, unicode_literals

import logging

from concurrency.config import conf

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
    return obj._concurrencymeta.field.attname


def _set_version(obj, version):
    """
    Set the given version on the passed object

    This function should be used with 'raw' values, any type conversion should be managed in
    VersionField._set_version_value(). This is needed for future enhancement of concurrency.
    """
    obj._concurrencymeta.field._set_version_value(obj, version)


def _select_lock(model_instance, version_value=None):
    if (not conf.ENABLED):
        return

    version_field = model_instance._concurrencymeta.field
    value = version_value or getattr(model_instance, version_field.name)
    is_versioned = value != version_field.get_default()

    if model_instance.pk is not None and is_versioned:
        kwargs = {'pk': model_instance.pk, version_field.name: value}
        entry = model_instance.__class__._base_manager.filter(**kwargs)

        if not entry:
            logger.debug("Conflict detected on `{0}` pk:`{0.pk}`, "
                         "version `{1}` not found".format(model_instance, value))
            conf._callback(model_instance)


class ConcurrencyOptions:
    field = None
    versioned_save = False
    manually = False
    enabled = True
    base = None
    check_fields = None
    ignore_fields = None
    skip = False
    increment = True
    initial = None
