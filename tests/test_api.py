from django.contrib.auth.models import Group

import pytest
from demo.models import SimpleConcurrentModel
from demo.util import nextgroup, nextname

from concurrency.api import (
    apply_concurrency_check, get_revision_of_object, get_version, is_changed
)
from concurrency.exceptions import RecordModifiedError
from concurrency.fields import IntegerVersionField
from concurrency.utils import refetch


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
def test_apply_concurrency_check():
    apply_concurrency_check(Group, 'version', IntegerVersionField)

    instance, __ = Group.objects.get_or_create(name=next(nextgroup))
    instance.save()

    copy = refetch(instance)
    copy.save()

    with pytest.raises(RecordModifiedError):
        instance.save()
