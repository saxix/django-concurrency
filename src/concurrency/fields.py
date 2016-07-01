from __future__ import absolute_import, unicode_literals

import copy
import functools
import hashlib
import logging
import time
from collections import OrderedDict
from functools import update_wrapper

from django.db.models import signals
from django.db.models.fields import Field
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from concurrency import forms
from concurrency.api import get_revision_of_object
from concurrency.config import conf
from concurrency.core import ConcurrencyOptions
from concurrency.utils import refetch

try:
    from django.apps import apps

    get_model = apps.get_model
except ImportError:
    from django.db.models.loading import get_model

try:
    from django.db.models.signals import class_prepared, post_migrate
except:
    from django.db.models.signals import class_prepared, post_syncdb as post_migrate

logger = logging.getLogger(__name__)

OFFSET = int(time.mktime((2000, 1, 1, 0, 0, 0, 0, 0, 0)))


def class_prepared_concurrency_handler(sender, **kwargs):
    if hasattr(sender, '_concurrencymeta'):
        if sender != sender._concurrencymeta.base:
            origin = getattr(sender._concurrencymeta.base, '_concurrencymeta')
            local = copy.deepcopy(origin)
            setattr(sender, '_concurrencymeta', local)

        if hasattr(sender, 'ConcurrencyMeta'):
            sender._concurrencymeta.enabled = getattr(sender.ConcurrencyMeta, 'enabled', True)
            check_fields = getattr(sender.ConcurrencyMeta, 'check_fields', None)
            ignore_fields = getattr(sender.ConcurrencyMeta, 'ignore_fields', None)
            if check_fields and ignore_fields:
                raise ValueError("Cannot set both 'check_fields' and 'ignore_fields'")

            sender._concurrencymeta.check_fields = check_fields
            sender._concurrencymeta.ignore_fields = ignore_fields
            sender._concurrencymeta.increment = getattr(sender.ConcurrencyMeta, 'increment', True)
            sender._concurrencymeta.skip = False

        if not (sender._concurrencymeta.manually):
            sender._concurrencymeta.field.wrap_model(sender)

        setattr(sender, 'get_concurrency_version', get_revision_of_object)


def post_syncdb_concurrency_handler(sender, **kwargs):
    from concurrency.triggers import create_triggers
    from django.db import connections

    databases = [alias for alias in connections]
    create_triggers(databases)


class_prepared.connect(class_prepared_concurrency_handler, dispatch_uid='class_prepared_concurrency_handler')


class TriggerRegistry(object):
    # FIXME: this is very bad. it seems required only by tests
    # see
    # https://github.com/pytest-dev/pytest-django/issues/75
    # https://code.djangoproject.com/ticket/22280#comment:20

    _fields = []

    def append(self, field):
        self._fields.append([field.model._meta.app_label, field.model.__name__])

    def __iter__(self):
        return iter([get_model(*i)._concurrencymeta.field for i in self._fields])

    def __contains__(self, field):
        target = [field.model._meta.app_label, field.model.__name__]
        return target in self._fields


_TRIGGERS = TriggerRegistry()

if not conf.MANUAL_TRIGGERS:
    post_migrate.connect(post_syncdb_concurrency_handler, dispatch_uid='post_syncdb_concurrency_handler')


class VersionField(Field):
    """ Base class """

    def __init__(self, *args, **kwargs):
        verbose_name = kwargs.get('verbose_name', None)
        name = kwargs.get('name', None)
        db_tablespace = kwargs.get('db_tablespace', None)
        db_column = kwargs.get('db_column', None)
        help_text = kwargs.get('help_text', _('record revision number'))

        super(VersionField, self).__init__(verbose_name, name,
                                           help_text=help_text,
                                           default=0,
                                           db_tablespace=db_tablespace,
                                           db_column=db_column)

    def deconstruct(self):
        name, path, args, kwargs = super(VersionField, self).deconstruct()
        kwargs['default'] = 1
        return name, path, args, kwargs

    def get_default(self):
        return 0

    def get_internal_type(self):
        return "BigIntegerField"

    def to_python(self, value):
        return int(value)

    def validate(self, value, model_instance):
        pass

    def formfield(self, **kwargs):
        kwargs['form_class'] = self.form_class
        kwargs['widget'] = forms.VersionField.widget
        return super(VersionField, self).formfield(**kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(VersionField, self).contribute_to_class(cls, name, virtual_only)
        if hasattr(cls, '_concurrencymeta') or cls._meta.abstract:
            return
        setattr(cls, '_concurrencymeta', ConcurrencyOptions())
        cls._concurrencymeta.field = self
        cls._concurrencymeta.base = cls

    def _set_version_value(self, model_instance, value):
        setattr(model_instance, self.attname, int(value))

    def pre_save(self, model_instance, add):
        if add:
            value = self._get_next_version(model_instance)
            self._set_version_value(model_instance, value)
        return getattr(model_instance, self.attname)

    @classmethod
    def wrap_model(cls, model, force=False):
        if not force and model._concurrencymeta.versioned_save:
            return
        cls._wrap_model_methods(model)
        model._concurrencymeta.versioned_save = True

    @staticmethod
    def _wrap_model_methods(model):
        old_do_update = getattr(model, '_do_update')
        setattr(model, '_do_update', model._concurrencymeta.field._wrap_do_update(old_do_update))

    def _wrap_do_update(self, func):

        def _do_update(model_instance, base_qs, using, pk_val, values, update_fields, forced_update):
            version_field = model_instance._concurrencymeta.field
            old_version = get_revision_of_object(model_instance)

            if not version_field.model._meta.abstract:
                if version_field.model is not base_qs.model:
                    return func(model_instance, base_qs, using, pk_val, values, update_fields, forced_update)

            for i, (field, _1, value) in enumerate(values):
                if field == version_field:
                    if (model_instance._concurrencymeta.increment and not
                    getattr(model_instance, '_concurrency_disable_increment', False)):
                        new_version = field._get_next_version(model_instance)
                        values[i] = (field, _1, new_version)
                        field._set_version_value(model_instance, new_version)
                    # else:
                    #     new_version = old_version
                    break

            # This provides a default if either (1) no values were provided or (2) we reached this code as part of a
            # create.  We don't need to worry about a race condition because a competing create should produce an
            # error anyway.
            updated = base_qs.filter(pk=pk_val).exists()

            # This second situation can occur because `Model.save_base` calls `Model._save_parent` without relaying
            # the `force_insert` flag that marks the process as a create.  Eventually, `Model._save_table` will call
            # this function as-if it were in the middle of an update.  The update is expected to fail because there
            # is no object to update and the caller will fall back on the create logic instead.  We need to ensure
            # the update fails (but does not raise an exception) under this circumstance by skipping the concurrency
            # logic.
            if values and updated:
                if (model_instance._concurrencymeta.enabled and
                        conf.ENABLED and
                        not getattr(model_instance, '_concurrency_disabled', False) and
                        (old_version or not conf.IGNORE_DEFAULT)):
                    filter_kwargs = {'pk': pk_val, version_field.attname: old_version}
                    updated = base_qs.filter(**filter_kwargs)._update(values) >= 1
                    if not updated:
                        version_field._set_version_value(model_instance, old_version)
                        updated = conf._callback(model_instance)
                else:
                    filter_kwargs = {'pk': pk_val}
                    updated = base_qs.filter(**filter_kwargs)._update(values) >= 1

            return updated

        return update_wrapper(_do_update, func)


class IntegerVersionField(VersionField):
    """
        Version Field that returns a "unique" version number for the record.

        The version number is produced using time.time() * 1000000, to get the benefits
        of microsecond if the system clock provides them.

    """
    form_class = forms.VersionField

    def _get_next_version(self, model_instance):
        old_value = getattr(model_instance, self.attname, 0)
        return max(int(old_value) + 1, (int(time.time() * 1000000) - OFFSET))


class AutoIncVersionField(VersionField):
    """
        Version Field increment the revision number each commit

    """
    form_class = forms.VersionField

    def _get_next_version(self, model_instance):
        return int(getattr(model_instance, self.attname, 0)) + 1


class TriggerVersionField(VersionField):
    """
        Version Field increment the revision number each commit

    """
    form_class = forms.VersionField

    def __init__(self, *args, **kwargs):
        self._trigger_name = kwargs.pop('trigger_name', None)
        self._trigger_exists = False
        super(TriggerVersionField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(TriggerVersionField, self).contribute_to_class(cls, name)
        if not cls._meta.abstract or cls._meta.proxy:
            if self not in _TRIGGERS:
                _TRIGGERS.append(self)

    def check(self, **kwargs):
        errors = []
        model = self.model
        from django.db import router, connections
        from concurrency.triggers import factory
        from django.core.checks import Warning

        alias = router.db_for_write(model)
        connection = connections[alias]
        f = factory(connection)
        if not f.get_trigger(self):
            errors.append(
                Warning(
                    'Missed trigger for field {}'.format(self),
                    hint=None,
                    obj=None,
                    id='concurrency.W001',
                )
            )
        return errors

    @property
    def trigger_name(self):
        from concurrency.triggers import get_trigger_name

        return get_trigger_name(self)

    def _get_next_version(self, model_instance):
        # always returns the same value
        return int(getattr(model_instance, self.attname, 1))

    def pre_save(self, model_instance, add):
        # always returns the same value
        return 1

    @staticmethod
    def _increment_version_number(obj):
        old_value = get_revision_of_object(obj)
        setattr(obj, obj._concurrencymeta.field.attname, int(old_value) + 1)

    @staticmethod
    def _wrap_model_methods(model):
        super(TriggerVersionField, TriggerVersionField)._wrap_model_methods(model)
        old_save = getattr(model, 'save')
        setattr(model, 'save', model._concurrencymeta.field._wrap_save(old_save))

    @staticmethod
    def _wrap_save(func):
        def inner(self, force_insert=False, force_update=False, using=None, **kwargs):
            reload = kwargs.pop('refetch', False)
            ret = func(self, force_insert, force_update, using, **kwargs)
            TriggerVersionField._increment_version_number(self)
            if reload:
                ret = refetch(self)
                setattr(self,
                        self._concurrencymeta.field.attname,
                        get_revision_of_object(ret))
            return ret

        return update_wrapper(inner, func)


def filter_fields(instance, field):
    if not field.concrete:
        # reverse relation
        return False
    if field.is_relation and field.related_model is None:
        # generic foreignkeys
        return False
    if field.many_to_many and instance.pk is None:
        # can't load remote object yet
        return False
    return True


class ConditionalVersionField(AutoIncVersionField):
    def contribute_to_class(self, cls, name, virtual_only=False):
        super(ConditionalVersionField, self).contribute_to_class(cls, name, virtual_only)
        signals.post_init.connect(self._load_model,
                                  sender=cls, weak=False)

        signals.post_save.connect(self._save_model,
                                  sender=cls, weak=False)

    def _load_model(self, *args, **kwargs):
        instance = kwargs['instance']
        instance._concurrencymeta.initial = self._get_hash(instance)

    def _save_model(self, *args, **kwargs):
        instance = kwargs['instance']
        instance._concurrencymeta.initial = self._get_hash(instance)

    def _get_hash(self, instance):
        values = OrderedDict()
        opts = instance._meta
        check_fields = instance._concurrencymeta.check_fields
        ignore_fields = instance._concurrencymeta.ignore_fields

        filter_ = functools.partial(filter_fields, instance)
        if check_fields is None and ignore_fields is None:
            fields = sorted([f.name for f in filter(filter_, instance._meta.get_fields())])
        elif check_fields is None:
            fields = sorted([f.name for f in filter(filter_, instance._meta.get_fields())
                             if f.name not in ignore_fields])
        else:
            fields = instance._concurrencymeta.check_fields

        for field_name in fields:
            # do not use getattr here. we do not need extra sql to retrieve
            # FK. the raw value of the FK is enough
            values[field_name] = opts.get_field(field_name).value_from_object(instance)
        return hashlib.sha1(force_text(values).encode('utf-8')).hexdigest()

    def _get_next_version(self, model_instance):
        if not model_instance.pk:
            return int(getattr(model_instance, self.attname) + 1)

        old = model_instance._concurrencymeta.initial
        new = self._get_hash(model_instance)
        if old != new:
            return int(getattr(model_instance, self.attname, 0) + 1)

        return int(getattr(model_instance, self.attname, 0))
