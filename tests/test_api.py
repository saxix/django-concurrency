from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
import pytest
from django.contrib.auth.models import Permission
from concurrency.api import (get_revision_of_object, is_changed, get_version,
                             apply_concurrency_check, disable_concurrency)
from concurrency.exceptions import RecordModifiedError
from concurrency.fields import IntegerVersionField
from tests.models import SimpleConcurrentModel
from tests.util import refetch, text


@pytest.mark.django_db
def test_get_revision_of_object(model_class=SimpleConcurrentModel):
    instance = model_class(username=text(10))
    instance.save()
    assert get_revision_of_object(instance) == instance.version


@pytest.mark.django_db
def test_is_changed(model_class=SimpleConcurrentModel):
    instance = model_class(username=text(10))
    instance.save()
    copy = refetch(instance)
    copy.save()
    assert is_changed(instance)


@pytest.mark.django_db
def test_get_version(model_class=SimpleConcurrentModel):
    instance = model_class(username=text(10))
    instance.save()
    copy = refetch(instance)
    copy.save()
    instance = get_version(instance, copy.version)
    assert instance.get_concurrency_version() == copy.get_concurrency_version()


@pytest.mark.django_db
def test_apply_concurrency_check(model_class=SimpleConcurrentModel):
    try:
        apply_concurrency_check(Permission, 'version', IntegerVersionField)
    except ImproperlyConfigured:
        pass

@pytest.mark.django_db(transaction=False)
def test_disable_concurrency(model_class=SimpleConcurrentModel):
    instance = model_class(username=text(10))
    instance.save()
    copy = refetch(instance)
    copy.save()
    with disable_concurrency(instance):
        instance.save()
