from contextlib import contextmanager
from functools import partial
import pytest
from sample_data_utils.utils import unique
from concurrency.config import conf
from sample_data_utils.sample import text
from tests.models import *  # noqa
from itertools import count

unique_name = unique(text, 1)
unique_id = count(1)


def refetch(model_instance):
    """
    Reload model instance from the database
    """
    return model_instance.__class__.objects.get(pk=model_instance.pk)


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

    new_kwargs = dict([(name, getattr(model_instance, name)) for name in fieldnames])
    return model_instance.__class__(**new_kwargs)


def models_parametrize(*models):
    ids = [m.__name__ for m in models]
    return pytest.mark.parametrize(('model_class,'),
                                   models,
                                   False,
                                   ids,
                                   None)


with_all_models = partial(models_parametrize, SimpleConcurrentModel, AutoIncConcurrentModel,
                          ProxyModel, InheritedModel,
                          CustomSaveModel, ConcreteModel)()

# with_all_models = partial(models_parametrize, ConcreteModel)()

DELETE_ATTRIBUTE = object()
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
    def set(target, name, value):
        if value is DELETE_ATTRIBUTE:
            delattr(target, name)
        else:
            setattr(target, name, value)

    backups = []

    for target, name, value in values:
        backups.append((target, name, getattr(target, name, DELETE_ATTRIBUTE)))
        set(target, name, value)
    yield
    for target, name, value in backups:
        set(target, name, value)
