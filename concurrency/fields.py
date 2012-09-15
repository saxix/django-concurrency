import time
import logging
import random
from django.db.models.fields import BigIntegerField
from . import core
from . import forms

logger = logging.getLogger('concurrency')

OFFSET = int(time.mktime([2000, 1, 1, 0, 0, 0, 0, 0, 0]))


class VersionField(core.VersionFieldMixin):
    """ Base class """


class IntegerVersionField(VersionField, BigIntegerField):
    """
        Version Field that returns a "unique" version number for the record.

        The version number is produced using time.time() * 1000000, to get the benefits
        of microsecond if the system clock provides them. @see `time.time()`.

    """
    def _REVISION_GET_NEXT(self, cls, field):
        value = getattr(cls, field.attname)
        return max(value + 1, (int(time.time() * 1000000) - OFFSET))

    def validate(self, value, model_instance):
        pass

    def formfield(self, **kwargs):
        kwargs['form_class'] = forms.VersionField
        kwargs['widget'] = forms.VersionField.widget
        return super(BigIntegerField, self).formfield(**kwargs)


class AutoIncVersionField(IntegerVersionField):
    """
        Version Field that returns a autoincrementatal integer as revision number.

    """
    def _REVISION_GET_NEXT(self, cls, field):
        value = getattr(cls, field.attname)
        return value + 1


class RandomVersionField(IntegerVersionField):
    """
        Version Field that returns a random revision number.
    """
    def _REVISION_GET_NEXT(self, cls, field):
        value = getattr(cls, field.attname)
        return random.randint(1, IntegerVersionField.MAX_BIGINT)


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
