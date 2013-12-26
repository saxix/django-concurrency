# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import warnings
from django.core.exceptions import ImproperlyConfigured
from django.db import router, connections
from django.db.models.loading import get_models, get_apps
import sys
from concurrency.exceptions import RecordModifiedError


logger = logging.getLogger(__name__)


def deprecated(replacement=None, version=None):
    """A decorator which can be used to mark functions as deprecated.
    replacement is a callable that will be called with the same args
    as the decorated function.

    >>> @deprecated()
    ... def foo(x):
    ...     return x
    ...
    >>> ret = foo(1)
    DeprecationWarning: foo is deprecated
    >>> ret
    1
    >>>
    >>>
    >>> def newfun(x):
    ...     return 0
    ...
    >>> @deprecated(newfun)
    ... def foo(x):
    ...     return x
    ...
    >>> ret = foo(1)
    DeprecationWarning: foo is deprecated; use newfun instead
    >>> ret
    0
    >>>
    """

    def outer(oldfun):  # pragma: no cover
        def inner(*args, **kwargs):
            msg = "%s is deprecated" % oldfun.__name__
            if version is not None:
                msg += "will be removed in version %s;" % version
            if replacement is not None:
                msg += "; use %s instead" % (replacement)
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            if callable(replacement):
                return replacement(*args, **kwargs)
            else:
                return oldfun(*args, **kwargs)

        return inner

    return outer


class ConcurrencyTestMixin(object):
    """
    Mixin class to test Models that use `VersionField`

    this class offer a simple test scenario. Its purpose is to discover
    some conflict in the `save()` inheritance::

        from concurrency.utils import ConcurrencyTestMixin
        from myproject.models import MyModel

        class MyModelTest(ConcurrencyTestMixin, TestCase):
            concurrency_model = TestModel0
            concurrency_kwargs = {'username': 'test'}

    """

    concurrency_model = None
    concurrency_kwargs = {}

    def _get_concurrency_target(self, **kwargs):
        # WARNING this method must be idempotent. ie must returns
        # always a fresh copy of the record
        args = dict(self.concurrency_kwargs)
        args.update(kwargs)
        return self.concurrency_model.objects.get_or_create(**args)[0]

    def test_concurrency_conflict(self):
        import concurrency.api as api

        target = self._get_concurrency_target()
        target_copy = self._get_concurrency_target()
        v1 = api.get_revision_of_object(target)
        v2 = api.get_revision_of_object(target_copy)
        assert v1 == v2, "got same row with different version (%s/%s)" % (v1, v2)
        target.save()
        assert target.pk is not None  # sanity check
        self.assertRaises(RecordModifiedError, target_copy.save)

    def test_concurrency_safety(self):
        import concurrency.api as api

        target = self.concurrency_model()
        version = api.get_revision_of_object(target)
        self.assertFalse(bool(version), "version is not null %s" % version)

    def test_concurrency_management(self):
        target = self.concurrency_model
        self.assertTrue(hasattr(target, '_concurrencymeta'),
                        "%s is not under concurrency management" % self.concurrency_model)
        info = getattr(target, '_concurrencymeta', None)
        revision_field = info._field

        self.assertTrue(revision_field in target._meta.fields,
                        "%s: version field not in meta.fields" % self.concurrency_model)


class ConcurrencyAdminTestMixin(object):
    pass


def get_triggers(databases):
    triggers = {}
    for alias in databases:
        connection = connections[alias]
        if hasattr(connection, 'list_triggers'):
            triggers[alias] = [trigger_name for trigger_name in connection.list_triggers()]
    return triggers


def drop_triggers(databases, stdout=sys.stdout):
    triggers = {}
    for alias in databases:
        connection = connections[alias]
        if hasattr(connection, 'drop_triggers'):
            connection.drop_triggers()

    return triggers


def create_triggers(databases, stdout=sys.stdout):
    from concurrency.fields import TriggerVersionField

    for app in get_apps():
        for model in get_models(app):
            if hasattr(model, '_concurrencymeta') and \
                    isinstance(model._concurrencymeta._field, TriggerVersionField):
                # stdout.write('Found concurrent model `%s`\n' % model.__name__)
                alias = router.db_for_write(model)
                if alias in databases:
                    connection = connections[alias]
                    if hasattr(connection.creation, '_create_trigger'):
                        connections[alias].creation._create_trigger(model._concurrencymeta._field)
                        # stdout.write('\tCreated trigger`%s`\n' % name)
                    else:
                        raise ImproperlyConfigured('TriggerVersionField need concurrency database backend')


def refetch(model_instance):
    """
    Reload model instance from the database
    """
    return model_instance.__class__.objects.get(pk=model_instance.pk)
