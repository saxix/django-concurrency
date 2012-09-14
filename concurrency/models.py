from django.db import models
import logging
from django.db import DatabaseError
from django.utils.translation import ugettext as _

logger = logging.getLogger('concurrency')


class RecordModifiedError(DatabaseError):
    pass


class ConcurrentModelManager(models.Manager):
    """
    """
#    def get_or_create(self, **kwargs):
#        if 'pk' in kwargs:
#            pass
#        else:
#            super(ConcurrentModelManager).get_or_create(**kwargs)


def lookup_revision(cls):
    for c, fk in cls._meta.parents.items():
        if hasattr(c, 'RevisionMetaInfo'):
            return c.RevisionMetaInfo.field, c
    if hasattr(cls, 'RevisionMetaInfo'):
        return cls.RevisionMetaInfo.field, cls
    return None, None


def save(self, force_insert=False, force_update=False, using=None):
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

