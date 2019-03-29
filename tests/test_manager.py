import pytest
from demo.models import (
    AutoIncConcurrentModel, ConcreteModel, CustomSaveModel, InheritedModel, ProxyModel,
    SimpleConcurrentModel
)
from demo.util import nextname, unique_id, with_models, with_std_models

from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch


@pytest.mark.django_db
@with_std_models
def test_get_or_create(model_class):
    instance, __ = model_class.objects.get_or_create(pk=next(unique_id))
    assert instance.get_concurrency_version()
    instance.save()


@pytest.mark.django_db
@with_std_models
def test_get_or_create_with_pk(model_class):
    instance, __ = model_class.objects.get_or_create(pk=next(unique_id))
    assert instance.get_concurrency_version()
    instance.save()
    copy = refetch(instance)
    copy.save()
    with pytest.raises(RecordModifiedError):
        instance.save()
    assert copy.get_concurrency_version() > instance.get_concurrency_version()


@pytest.mark.django_db(transaction=False)
def test_create(model_class=SimpleConcurrentModel):
    instance = model_class.objects.create(pk=next(unique_id))
    assert instance.get_concurrency_version()


@pytest.mark.django_db
@with_models(SimpleConcurrentModel, AutoIncConcurrentModel,
             InheritedModel, CustomSaveModel,
             ConcreteModel, ProxyModel)
def test_update(model_class):
    # Manager.update() does not change version number
    instance = model_class.objects.create(pk=next(unique_id), username=next(nextname).lower())
    field_value = instance.username
    model_class.objects.filter(pk=instance.pk).update(username=instance.username.upper())

    instance2 = refetch(instance)
    assert instance2.username == field_value.upper()
    assert instance2.get_concurrency_version() == instance.get_concurrency_version()
