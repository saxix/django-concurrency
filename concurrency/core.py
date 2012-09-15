from django.db import DatabaseError
from django.utils.translation import ugettext as _
from django.utils.functional import curry


class RecordModifiedError(DatabaseError):
    pass


def versioned_save(self, force_insert=False, force_update=False, using=None):
    if force_insert and force_update:
        raise ValueError("Cannot force both insert and updating in model saving.")

    if self.pk and not force_insert:
        kwargs = {'pk': self.pk, self.RevisionMetaInfo.field.name: getattr(self, self.RevisionMetaInfo.field.name)}
        entry = self.__class__.objects.select_for_update().filter(**kwargs)
        if not entry:
            if getattr(self, self.RevisionMetaInfo.field.name) == 0:
                raise RecordModifiedError(_('Version field is 0 but record has `pk`.'))
            raise RecordModifiedError(_('Record has been modified'))

    self.version = self._revision_get_next()
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

    def _get_REVISION_NUMBER(self, cls, field):
        value = getattr(cls, field.attname)
        return value

    def _set_REVISION_NUMBER(self, instance, value):
        field = instance.RevisionMetaInfo.field
        setattr(instance, field.attname, value)

    def contribute_to_class(self, cls, name):
        super(VersionFieldMixin, self).contribute_to_class(cls, name)
        if hasattr(cls, 'RevisionMetaInfo'):
            return

        setattr(cls, '_get_revision_number', curry(self._get_REVISION_NUMBER, field=self))
        setattr(cls, '_set_revision_number', curry(self._set_REVISION_NUMBER))
        setattr(cls, '_revision_get_next', curry(self._REVISION_GET_NEXT, field=self))
        setattr(cls, 'save', versioned_save)
        setattr(cls, 'RevisionMetaInfo', RevisionMetaInfo())
        cls.RevisionMetaInfo.field = self

    def get_default(self):
        return 0
