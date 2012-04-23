from datetime import datetime
import logging
from django.utils.functional import curry
from django.db.models import IntegerField
from django.db.models.fields import DateTimeField
from django.db import DatabaseError
from django.utils.timezone import utc
from concurrency import models


logger = logging.getLogger('concurrency')

class RevisionMetaInfo:
    field = None

class VersionFieldMixin(object):
    def __init__(self, verbose_name=None, name=None, help_text='',
                 db_column=None, db_tablespace=None):
        super(VersionFieldMixin, self).__init__(verbose_name, name, editable=False,
            help_text=help_text,null=False, blank=False,
            db_tablespace=db_tablespace, db_column=db_column)

    def _get_REVISION_NUMBER(self, cls, field):
        value = getattr(cls, field.attname)
        return value

    def _set_REVISION_NUMBER(self, instance, value):
        field = instance.RevisionMetaInfo.field
        setattr(instance, field.attname, value)

    def contribute_to_class(self, cls, name):
        assert not hasattr(cls, 'RevisionMetaInfo'), "A model can't have more than one VersionField."
        super(VersionFieldMixin, self).contribute_to_class(cls, name)

#        if not self in opts.local_fields: return
#        opts = cls._meta

        setattr(cls, '_get_revision_number', curry(self._get_REVISION_NUMBER, field=self))
        setattr(cls, '_set_revision_number', curry(self._set_REVISION_NUMBER))
        setattr(cls, '_revision_get_next', curry(self._REVISION_GET_NEXT, field=self))
        setattr(cls, 'save_base', models.save_base)
        setattr(cls, 'RevisionMetaInfo', RevisionMetaInfo())
        cls.RevisionMetaInfo.field = self

    def get_default(self):
        return 0

class DateTimeVersionField(VersionFieldMixin, DateTimeField):
    def _REVISION_GET_NEXT(self, cls, field):
        return  datetime.utcnow().replace(tzinfo=utc)


class IntegerVersionField(VersionFieldMixin, IntegerField):
    def _REVISION_GET_NEXT(self, cls, field):
        value = getattr(cls, field.attname)
        return value + 1




