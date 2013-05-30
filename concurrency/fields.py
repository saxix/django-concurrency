import time
import logging
from django.utils.translation import ugettext as _
from django.db.models.fields import Field

from concurrency import forms
from concurrency.core import RevisionMetaInfo, _wrap_model_save

logger = logging.getLogger('concurrency')

OFFSET = int(time.mktime((2000, 1, 1, 0, 0, 0, 0, 0, 0)))


class VersionField(Field):
    """ Base class """

    def __init__(self, **kwargs):
        self.manually = kwargs.pop('manually', False)

        verbose_name = kwargs.get('verbose_name', None)
        name = kwargs.get('name', None)
        db_tablespace = kwargs.get('db_tablespace', None)
        db_column = kwargs.get('db_column', None)
        help_text = kwargs.get('help_text', _('record revision number'))

        super(VersionField, self).__init__(verbose_name, name, editable=True,
                                           help_text=help_text, null=False, blank=False,
                                           default=0,
                                           db_tablespace=db_tablespace, db_column=db_column)

    def get_default(self):
        return 0

    def validate(self, value, model_instance):
        pass

    def formfield(self, **kwargs):
        kwargs['form_class'] = self.form_class
        kwargs['widget'] = forms.VersionField.widget
        return super(VersionField, self).formfield(**kwargs)

    def contribute_to_class(self, cls, name):
        super(VersionField, self).contribute_to_class(cls, name)
        if hasattr(cls, 'RevisionMetaInfo'):
            return
        setattr(cls, 'RevisionMetaInfo', RevisionMetaInfo())
        _wrap_model_save(cls)
        cls.RevisionMetaInfo.field = self
        cls.RevisionMetaInfo.manually = self.manually


class IntegerVersionField(VersionField):
    """
        Version Field that returns a "unique" version number for the record.

        The version number is produced using time.time() * 1000000, to get the benefits
        of microsecond if the system clock provides them.

    """
    form_class = forms.VersionField

    def get_internal_type(self):
        return "BigIntegerField"

    def pre_save(self, model_instance, add):
        old_value = getattr(model_instance, self.attname) or 0
        value = max(old_value + 1, (int(time.time() * 1000000) - OFFSET))
        setattr(model_instance, self.attname, value)
        return value


class AutoIncVersionField(VersionField):
    """
        Version Field increment the revision number each commit

    """
    form_class = forms.VersionField

    def get_internal_type(self):
        return "BigIntegerField"

    def pre_save(self, model_instance, add):
        value = (getattr(model_instance, self.attname) or 0) + 1
        setattr(model_instance, self.attname, value)
        return value


try:
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

    add_introspection_rules(rules, [r"^concurrency\.fields\.IntegerVersionField",
                                    r"^concurrency\.fields\.AutoIncVersionField"])
except ImportError as e:
    from django.conf import settings

    if 'south' in settings.INSTALLED_APPS:
        raise e
