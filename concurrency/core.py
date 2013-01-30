from functools import update_wrapper
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError
from django.utils.translation import ugettext as _

__all__ = []


class RecordModifiedError(DatabaseError):
    pass


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


def concurrency_check(self, force_insert=False, force_update=False, using=None, **kwargs):
    if self.pk and not force_insert:
        _select_lock(self)
    field = self.RevisionMetaInfo.field
    setattr(self, field.attname, field.get_new_value(self))


def _select_lock(obj, version=None):
    kwargs = {'pk': obj.pk, obj.RevisionMetaInfo.field.name: version or getattr(obj, obj.RevisionMetaInfo.field.name)}
    entry = obj.__class__.objects.select_for_update(nowait=True).filter(**kwargs)
    if not entry:
        if getattr(obj, obj.RevisionMetaInfo.field.name) == 0:
            raise RecordModifiedError(_('Version field is 0 but record has `pk`.'))
        raise RecordModifiedError(_('Record has been modified'))


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

