from django.db import DatabaseError
from django.utils.translation import ugettext as _


class RecordModifiedError(DatabaseError):
    pass


def _select_lock(obj, version=None):
    kwargs = {'pk': obj.pk, obj.RevisionMetaInfo.field.name: version or getattr(obj, obj.RevisionMetaInfo.field.name) }
    entry = obj.__class__.objects.select_for_update(nowait=True).filter(**kwargs)
    if not entry:
        if getattr(obj, obj.RevisionMetaInfo.field.name) == 0:
            raise RecordModifiedError(_('Version field is 0 but record has `pk`.'))
        raise RecordModifiedError(_('Record has been modified'))

def _versioned_save(self, force_insert=False, force_update=False, using=None):
    if force_insert and force_update:
        raise ValueError("Cannot force both insert and updating in model saving.")

    if self.pk and not force_insert:
        _select_lock(self)
    field = self.RevisionMetaInfo.field
    setattr(self, field.attname, field.get_new_value(self))
    self.save_base(using=using, force_insert=force_insert, force_update=force_update)


class RevisionMetaInfo:
    field = None


class VersionFieldMixin(object):
    def __init__(self, **kwargs):
        verbose_name = kwargs.get('verbose_name', None)
        name = kwargs.get('name', None)
        db_tablespace = kwargs.get('db_tablespace', None)
        db_column = kwargs.get('db_column', None)
        help_text = kwargs.get('help_text', _('record revision number'))

        super(VersionFieldMixin, self).__init__(verbose_name, name, editable=True,
            help_text=help_text, null=False, blank=False, default=1,
            db_tablespace=db_tablespace, db_column=db_column)

    def contribute_to_class(self, cls, name):
        super(VersionFieldMixin, self).contribute_to_class(cls, name)
        if hasattr(cls, 'RevisionMetaInfo'):
            return

        setattr(cls, 'save', _versioned_save)
        setattr(cls, 'RevisionMetaInfo', RevisionMetaInfo())
        cls.RevisionMetaInfo.field = self

    def get_default(self):
        return 0
