import time
import logging
from django.utils.translation import ugettext as _
from django.db.models.fields import BigIntegerField
from concurrency import forms
from concurrency.core import RevisionMetaInfo

logger = logging.getLogger('concurrency')

OFFSET = int(time.mktime([2000, 1, 1, 0, 0, 0, 0, 0, 0]))


class VersionField(BigIntegerField):
    """ Base class """

    def __init__(self, **kwargs):
        self.manually = kwargs.pop('manually', False)

        verbose_name = kwargs.get('verbose_name', None)
        name = kwargs.get('name', None)
        db_tablespace = kwargs.get('db_tablespace', None)
        db_column = kwargs.get('db_column', None)
        help_text = kwargs.get('help_text', _('record revision number'))

        super(VersionField, self).__init__(verbose_name, name, editable=True,
                                           help_text=help_text, null=False, blank=False, default=1,
                                           db_tablespace=db_tablespace, db_column=db_column)

    def get_default(self):
        return 0

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
        cls.RevisionMetaInfo.manually = self.manually


class IntegerVersionField(VersionField):
    """
        Version Field that returns a "unique" version number for the record.

        The version number is produced using time.time() * 1000000, to get the benefits
        of microsecond if the system clock provides them.

    """

    def _REVISION_GET_NEXT(self, instance, field):
        value = getattr(instance, field.attname)
        return max(value + 1, (int(time.time() * 1000000) - OFFSET))


class AutoIncVersionField(VersionField):
    """
        Version Field increment the revision number each commit

    """

    def _REVISION_GET_NEXT(self, instance, field):
        value = getattr(instance, field.attname)
        return value + 1


try:
    import south
    from south.modelsinspector import add_introspection_rules

    rules = [
        (
            (IntegerVersionField, AutoIncVersionField),
            [], {"verbose_name": ["verbose_name", {"default": None}],
                 "name": ["name", {"default": None}],
                 "help_text": ["help_text", {"default": ''}],
                 "db_column": ["db_column", {"default": None}],
                 "db_tablespace": ["db_tablespace", {"default": None}],
                 "default": ["default", {"default": 0}],
                 "manually": ["manually", {"default": False}]})
    ]

    add_introspection_rules(rules, ["^concurrency\.fields\.IntegerVersionField",
                                    "^concurrency\.fields\.AutoIncVersionField"])
except ImportError as e:
    from django.conf import settings

    if 'south' in settings.INSTALLED_APPS:
        raise e
