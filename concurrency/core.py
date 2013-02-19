import warnings
from functools import update_wrapper
from django.conf import settings
from django.db import DatabaseError, connections, router
from django.utils.translation import ugettext as _
from concurrency.exceptions import VersionChangedError, RecordModifiedError, InconsistencyError

__all__ = []

def deprecate(target, subst, version):
    warnings.warn("`{0}` will be removed in version `{2}`. Please use `{1}`".format(target, subst, version),
                  category=DeprecationWarning)

def apply_concurrency_check(model, fieldname, versionclass):
    from concurrency.api import apply_concurrency_check as acc
    return acc(model, fieldname, versionclass)


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


def _wrap_save(func):
    def inner(self, force_insert=False, force_update=False, using=None, **kwargs):
        concurrency_check(self, force_insert, force_update, using, **kwargs)
        return func(self, force_insert, force_update, using, **kwargs)

    return update_wrapper(inner, func)


def _versioned_save(self, force_insert=False, force_update=False, using=None):
    if force_insert and force_update:
        raise ValueError("Cannot force both insert and updating in model saving.")
    concurrency_check(self, force_insert, force_update, using)
    self.save_base(using=using, force_insert=force_insert, force_update=force_update)


def class_prepared_concurrency_handler(sender, **kwargs):
    if hasattr(sender, 'RevisionMetaInfo') and not (sender.RevisionMetaInfo.manually or
                                                    sender.RevisionMetaInfo.versioned_save):
        old_save = getattr(sender, 'save')
        setattr(sender, 'save', _wrap_save(old_save))
        sender.RevisionMetaInfo.versioned_save = True


class RevisionMetaInfo:
    field = None
    versioned_save = False
    manually = False

