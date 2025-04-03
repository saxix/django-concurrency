import logging
from logging import NullHandler

from concurrency.config import conf

logging.getLogger("concurrency").addHandler(NullHandler())

logger = logging.getLogger(__name__)

__all__ = []


def get_version_fieldname(obj):
    return obj._concurrencymeta.field.attname


def _set_version(obj, version) -> None:
    """
    Set the given version on the passed object

    This function should be used with 'raw' values, any type conversion should be managed in
    VersionField._set_version_value(). This is needed for future enhancement of concurrency.
    """
    obj._concurrencymeta.field._set_version_value(obj, version)


def _select_lock(model_instance, version_value=None) -> None:
    if not conf.ENABLED:
        return

    version_field = model_instance._concurrencymeta.field
    value = version_value or getattr(model_instance, version_field.name)
    is_versioned = value != version_field.get_default()

    if model_instance.pk is not None and is_versioned:
        kwargs = {"pk": model_instance.pk, version_field.name: value}
        entry = model_instance.__class__._base_manager.filter(**kwargs)

        if not entry:
            logger.debug(
                f"Conflict detected on `{model_instance}` pk:`{model_instance.pk}`, version `{value}` not found"
            )
            conf._callback(model_instance)
        else:  # pragma: no cover
            pass
    else:  # pragma: no cover
        pass


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
    triggers = []
