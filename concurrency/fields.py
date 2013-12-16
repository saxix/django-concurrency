import time
import copy
import logging
from functools import update_wrapper
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import Field
from django.db.models.signals import class_prepared, post_syncdb

from concurrency import forms
from concurrency.config import conf, CONCURRENCY_POLICY_CALLBACK
from concurrency.core import ConcurrencyOptions, _wrap_model_save
from concurrency.api import get_revision_of_object
from concurrency.exceptions import RecordModifiedError, InconsistencyError

logger = logging.getLogger(__name__)

OFFSET = int(time.mktime((2000, 1, 1, 0, 0, 0, 0, 0, 0)))


def class_prepared_concurrency_handler(sender, **kwargs):
    if hasattr(sender, '_concurrencymeta'):
        origin = getattr(sender._concurrencymeta._base, '_concurrencymeta')
        local = copy.deepcopy(origin)
        setattr(sender, '_concurrencymeta', local)

        if hasattr(sender, 'ConcurrencyMeta'):
            sender._concurrencymeta.enabled = getattr(sender.ConcurrencyMeta, 'enabled')

        if not (sender._concurrencymeta._manually):
            _wrap_model_save(sender)
        from concurrency.api import get_version, get_object_with_version

        setattr(sender._default_manager.__class__,
                'get_object_with_version', get_object_with_version)
        setattr(sender, 'get_concurrency_version', get_version)
    else:
        logger.debug('Skipped concurrency for %s' % sender)


class_prepared.connect(class_prepared_concurrency_handler, dispatch_uid='class_prepared_concurrency_handler')


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

    def to_python(self, value):
        return int(value)

    def validate(self, value, model_instance):
        pass

    def formfield(self, **kwargs):
        kwargs['form_class'] = self.form_class
        kwargs['widget'] = forms.VersionField.widget
        return super(VersionField, self).formfield(**kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(VersionField, self).contribute_to_class(cls, name)
        if hasattr(cls, '_concurrencymeta'):
            return
        setattr(cls, '_concurrencymeta', ConcurrencyOptions())
        cls._concurrencymeta._field = self
        cls._concurrencymeta._base = cls
        cls._concurrencymeta._manually = self.manually

    def _set_version_value(self, model_instance, value):
        setattr(model_instance, self.attname, int(value))


    def _wrap_do_insert(self, func):
        def _do_insert(model_instance, manager, using, fields, update_pk, raw):
            #FIXME: is SANITY_CHECK related code required ?
            if [f for f in fields if isinstance(f, VersionField)]:
                version_field = model_instance._concurrencymeta._field
                value = get_revision_of_object(model_instance)
                is_versioned = value != version_field.get_default()

                if is_versioned and conf.SANITY_CHECK and model_instance._concurrencymeta.sanity_check:
                    raise InconsistencyError(_('Version field is set (%s) but record has not `pk`.') % value)


                self._set_version_value(model_instance, self._get_next_version(model_instance))
            ret = func(model_instance, manager, using, fields, update_pk, raw)
            return ret
        return update_wrapper(_do_insert, func)


    def _wrap_do_update(self, func):
        def _do_update(model_instance, base_qs, using, pk_val, values, update_fields, forced_update):
            version_field = model_instance._concurrencymeta._field
            version = get_revision_of_object(model_instance)
            if version_field.model != base_qs.model:
                return func(model_instance, base_qs, using, pk_val, values, update_fields, forced_update)
            if values:
                filter_kwargs = {'pk': pk_val, version_field.attname: version}
                for i, (field, _1, value) in enumerate(values):
                    if isinstance(field, VersionField):
                        new_version = field._get_next_version(model_instance)
                        values[i] = (field, _1, new_version)
                        field._set_version_value(model_instance, new_version)
                        break
                if version == version_field.get_default():
                    return func(model_instance, base_qs, using, pk_val, values, update_fields, forced_update)

                updated = base_qs.filter(**filter_kwargs)._update(values) >= 1
                if not updated:
                    if conf.POLICY & CONCURRENCY_POLICY_CALLBACK:
                        return conf._callback(model_instance)
                    else:
                        raise RecordModifiedError(target=model_instance)
            else:
                updated = base_qs.filter(pk=pk_val).exists()

            return updated

        return update_wrapper(_do_update, func)


class IntegerVersionField(VersionField):
    """
        Version Field that returns a "unique" version number for the record.

        The version number is produced using time.time() * 1000000, to get the benefits
        of microsecond if the system clock provides them.

    """
    form_class = forms.VersionField

    def get_internal_type(self):
        return "BigIntegerField"

    def _get_next_version(self, model_instance):
        old_value = getattr(model_instance, self.attname, 0)
        return max(int(old_value) + 1, (int(time.time() * 1000000) - OFFSET))

    def pre_save(self, model_instance, add):
        if model_instance._concurrencymeta._protocol >= 2:
            return getattr(model_instance, self.attname)

        value = self._get_next_version(model_instance)
        self._set_version_value(model_instance, value)
        return value

    @staticmethod
    def _wrap_save(func):
        from concurrency.api import concurrency_check

        def inner(self, force_insert=False, force_update=False, using=None, **kwargs):
            if self._concurrencymeta.enabled:
                concurrency_check(self, force_insert, force_update, using, **kwargs)
            return func(self, force_insert, force_update, using, **kwargs)

        return update_wrapper(inner, func)


class AutoIncVersionField(VersionField):
    """
        Version Field increment the revision number each commit

    """
    form_class = forms.VersionField

    def get_internal_type(self):
        return "BigIntegerField"

    def _get_next_version(self, model_instance):
        return int(getattr(model_instance, self.attname, 0)) + 1

    def pre_save(self, model_instance, add):
        if model_instance._concurrencymeta._protocol >= 2:
            return getattr(model_instance, self.attname)
        value = self._get_next_version(model_instance)
        self._set_version_value(model_instance, value)
        return value

    @staticmethod
    def _wrap_save(func):
        from concurrency.api import concurrency_check

        def inner(self, force_insert=False, force_update=False, using=None, **kwargs):
            if self._concurrencymeta.enabled:
                concurrency_check(self, force_insert, force_update, using, **kwargs)
            return func(self, force_insert, force_update, using, **kwargs)

        return update_wrapper(inner, func)


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
