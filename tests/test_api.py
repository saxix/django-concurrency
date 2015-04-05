import pytest
from django.contrib.auth.models import Permission, Group
from concurrency.fields import AutoIncVersionField, IntegerVersionField
from concurrency.exceptions import RecordModifiedError
from concurrency.api import (get_revision_of_object, is_changed, get_version,
                             disable_concurrency, apply_concurrency_check)
from concurrency.utils import refetch
from demo.models import SimpleConcurrentModel
from demo.util import nextname, nextgroup


@pytest.mark.django_db(transaction=False)
@pytest.mark.skipIf('os.environ["DBENGINE"]=="pg"')
def test_get_revision_of_object(model_class=SimpleConcurrentModel):
    instance = model_class(username=next(nextname))
    instance.save()
    assert get_revision_of_object(instance) == instance.version


@pytest.mark.django_db
def test_is_changed(model_class=SimpleConcurrentModel):
    instance = model_class(username=next(nextname))
    instance.save()
    copy = refetch(instance)
    copy.save()
    assert is_changed(instance)


@pytest.mark.django_db
def test_get_version(model_class=SimpleConcurrentModel):
    instance = model_class(username=next(nextname))
    instance.save()
    copy = refetch(instance)
    copy.save()
    instance = get_version(instance, copy.version)
    assert instance.get_concurrency_version() == copy.get_concurrency_version()


@pytest.mark.django_db(transaction=False)
def test_disable_concurrency(model_class=SimpleConcurrentModel):
    instance = model_class(username=next(nextname))
    instance.save()
    copy = refetch(instance)
    copy.save()
    with disable_concurrency(SimpleConcurrentModel):
        instance.save()


@pytest.mark.django_db(transaction=False)
def test_disable_concurrency_specific_model(model_class=SimpleConcurrentModel):
    instance1 = model_class(username=next(nextname))
    instance1.save()
    copy1 = refetch(instance1)
    copy1.save()

    instance2 = model_class(username=next(nextname))
    instance2.save()
    copy2 = refetch(instance2)
    copy2.save()

    with disable_concurrency(instance1):
        instance1.save()
        with pytest.raises(RecordModifiedError):
            instance2.save()


@pytest.mark.django_db(transaction=False)
def test_apply_concurrency_check():
    apply_concurrency_check(Group, 'version', IntegerVersionField)

    instance, __ = Group.objects.get_or_create(name=next(nextgroup))
    instance.save()

    copy = refetch(instance)
    copy.save()

    with pytest.raises(RecordModifiedError):
        instance.save()


