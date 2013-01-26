import time
import logging
import random
from django.db.models.fields import BigIntegerField
from . import core
from . import forms
from concurrency.core import _versioned_save, RevisionMetaInfo

logger = logging.getLogger('concurrency')

OFFSET = int(time.mktime([2000, 1, 1, 0, 0, 0, 0, 0, 0]))


class VersionField(core.VersionFieldMixin):
    """ Base class """

    def get_new_value(self, obj):
        return self._REVISION_GET_NEXT(obj, self)

    def validate(self, value, model_instance):
        pass

    def formfield(self, **kwargs):
        kwargs['form_class'] = forms.VersionField
        kwargs['widget'] = forms.VersionField.widget
        return super(VersionField, self).formfield(**kwargs)

    def contribute_to_class(self, cls, name):
        super(VersionField, self).contribute_to_class(cls, name)
        if hasattr(cls, 'RevisionMetaInfo'):
            return
        setattr(cls, 'RevisionMetaInfo', RevisionMetaInfo())
        cls.RevisionMetaInfo.field = self

class VersionSaveMixin(object):
    def contribute_to_class(self, cls, name):
        super(VersionSaveMixin, self).contribute_to_class(cls, name)
        if cls.RevisionMetaInfo.versioned_save:
            return
        setattr(cls, 'save', _versioned_save)
        cls.RevisionMetaInfo.versioned_save = True


class RawIntegerVersionField(VersionField, BigIntegerField):
    """
        Version Field that returns a "unique" version number for the record.

        The version number is produced using time.time() * 1000000, to get the benefits
        of microsecond if the system clock provides them. :ref:`py:time.time`.

    """
    def _REVISION_GET_NEXT(self, instance, field):
        value = getattr(instance, field.attname)
        return max(value + 1, (int(time.time() * 1000000) - OFFSET))


class RawAutoIncVersionField(VersionField, BigIntegerField):
    """
        Version Field increment the revision number each commit

    """
    def _REVISION_GET_NEXT(self, instance, field):
        value = getattr(instance, field.attname)
        return value + 1

class IntegerVersionField(VersionSaveMixin, RawIntegerVersionField):
    pass


class AutoIncVersionField(VersionSaveMixin, RawAutoIncVersionField):
    pass

try:
    import south
    from south.modelsinspector import add_introspection_rules

    rules = [
        (
            (IntegerVersionField, ),
            [],
            {
                "verbose_name": ["verbose_name", {"default": None}],
                "name": ["name", {"default": None}],
                "help_text": ["help_text", {"default": ''}],
                "db_column": ["db_column", {"default": None}],
                "db_tablespace": ["db_tablespace", {"default": None}],
                "default": ["default", {"default": 0}],
            })
    ]

    add_introspection_rules(rules, ["^concurrency\.fields\.IntegerVersionField"])
except ImportError:
    pass
