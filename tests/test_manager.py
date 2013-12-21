import pytest
from concurrency.exceptions import RecordModifiedError
from tests.util import refetch, text, with_all_models, unique_id


@pytest.mark.django_db
@with_all_models
def test_get_or_create(model_class):
    instance, __ = model_class.objects.get_or_create(username=text(10))
    assert instance.get_concurrency_version()
    instance.save()


@pytest.mark.django_db
@with_all_models
def test_get_or_create_with_pk(model_class):
    instance, __ = model_class.objects.get_or_create(pk=next(unique_id))
    assert instance.get_concurrency_version()
    instance.save()
    copy = refetch(instance)
    copy.save()
    with pytest.raises(RecordModifiedError):
        instance.save()
    assert copy.get_concurrency_version() > instance.get_concurrency_version()


@pytest.mark.django_db
@with_all_models
def test_create(model_class):
    instance = model_class.objects.create(username=text(10))
    assert instance.get_concurrency_version()


@pytest.mark.django_db
@with_all_models
def test_update(model_class):
    # Manager.update() does not change version number
    instance = model_class.objects.create(username=text(10).lower())
    field_value = instance.username
    model_class.objects.filter(pk=instance.pk).update(username=instance.username.upper())

    instance2 = refetch(instance)
    assert instance2.username == field_value.upper()
    assert instance2.get_concurrency_version() == instance.get_concurrency_version()
