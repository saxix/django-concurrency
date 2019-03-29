import itertools
from contextlib import contextmanager
from functools import partial, update_wrapper
from itertools import count

from django import db

import pytest
from demo.models import (
    AutoIncConcurrentModel, ConcreteModel, CustomSaveModel, InheritedModel, ProxyModel,
    SimpleConcurrentModel, TriggerConcurrentModel
)

from concurrency.config import conf


def sequence(prefix):
    infinite = itertools.count()
    while 1:
        yield "{0}-{1}".format(prefix, next(infinite))


nextname = sequence('username')
nextgroup = sequence('group')
unique_id = count(1)


def override_conf(**kwargs):
    for key, new_value in kwargs.items():
        setattr(conf, key, new_value)


def clone_instance(model_instance):
    """
        returns a copy of the passed instance.

        .. warning: All fields are copied, even primary key

    :param instance: :py:class:`django.db.models.Model` instance
    :return: :py:class:`django.db.models.Model` instance
    """

    fieldnames = [fld.name for fld in model_instance._meta.fields]

    new_kwargs = {name: getattr(model_instance, name) for name in fieldnames}
    return model_instance.__class__(**new_kwargs)


def with_models(*models, **kwargs):
    ignore = kwargs.pop('ignore', [])
    if ignore:
        models = filter(models, lambda x: x not in ignore)

    ids = [m.__name__ for m in models]

    return pytest.mark.parametrize(('model_class,'),
                                   models,
                                   False,
                                   ids,
                                   None)


MODEL_CLASSES = [SimpleConcurrentModel, AutoIncConcurrentModel,
                 InheritedModel, CustomSaveModel,
                 ConcreteModel, ProxyModel, TriggerConcurrentModel]

with_std_models = partial(with_models, SimpleConcurrentModel, AutoIncConcurrentModel,
                          InheritedModel, CustomSaveModel,
                          ConcreteModel, ProxyModel)()
with_all_models = partial(with_models, *MODEL_CLASSES)()

# with_all_models = partial(models_parametrize, ConcreteModel)()

DELETE_ATTRIBUTE = object()


@pytest.fixture(params=MODEL_CLASSES)
def concurrent_model(request):
    return request.param


@contextmanager
def attributes(*values):
    """
        context manager to temporary set/delete object's attributes
    :param values: tulples of (target, name, value)
    Es.


    with attributes((django.contrib.admin.ModelAdmin, 'list_per_page', 200)):
        ...

    with attributes((django.contrib.admin.ModelAdmin, 'list_per_page', DELETE_ATTRIBUTE)):
        ...

    """

    def _set(target, name, value):
        if value is DELETE_ATTRIBUTE:
            delattr(target, name)
        else:
            setattr(target, name, value)

    backups = []

    for target, name, value in values:
        if hasattr(target, name):
            backups.append((target, name, getattr(target, name)))
        else:
            backups.append((target, name, getattr(target, name, DELETE_ATTRIBUTE)))
        _set(target, name, value)
    yield

    for target, name, value in backups:
        _set(target, name, value)


def concurrently(times=1):
    # from: http://www.caktusgroup.com/blog/2009/05/26/testing-django-views-for-concurrency-issues/
    """
Add this decorator to small pieces of code that you want to test
concurrently to make sure they don't raise exceptions when run at the
same time. E.g., some Django views that do a SELECT and then a subsequent
INSERT might fail when the INSERT assumes that the data has not changed
since the SELECT.
"""

    def concurrently_decorator(test_func):
        def wrapper(*args, **kwargs):
            exceptions = []
            import threading

            def call_test_func():
                try:
                    test_func(*args, **kwargs)
                except Exception as e:
                    exceptions.append(e)
                    raise
                finally:
                    db.connection.close()

            threads = []
            for i in range(times):
                threads.append(threading.Thread(target=call_test_func))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            if exceptions:
                raise Exception(
                    'test_concurrently intercepted %s exceptions: %s' %
                    (len(exceptions), exceptions))

        return update_wrapper(wrapper, test_func)

    return concurrently_decorator
