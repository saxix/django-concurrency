from concurrency.fields import IntegerVersionField
from concurrency.api import apply_concurrency_check
import pytest
from django.contrib.auth.models import Group
from concurrency.core import _set_version
from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch
from tests.util import with_all_models, unique_id, nextname, with_std_models, nextgroup


pytest.mark.django_db(transaction=False)

@pytest.mark.django_db
@with_all_models
def test_standard_save(model_class):
    instance = model_class(username=next(nextname))
    instance.save()
    assert instance.get_concurrency_version() > 0


@pytest.mark.django_db(transaction=False)
@with_std_models
def test_conflict(model_class):
    id = next(unique_id)
    instance = model_class.objects.get_or_create(pk=id)[0]
    instance.save()

    copy = refetch(instance)
    copy.save()

    with pytest.raises(RecordModifiedError):
        instance.save()
    assert copy.get_concurrency_version() > instance.get_concurrency_version()


@pytest.mark.django_db(transaction=False)
@with_std_models
def test_do_not_check_if_no_version(model_class):
    id = next(unique_id)
    instance, __ = model_class.objects.get_or_create(pk=id)
    instance.save()

    copy = refetch(instance)
    copy.save()

    with pytest.raises(RecordModifiedError):
        _set_version(instance, 1)
        instance.version = 1
        instance.save()

    _set_version(instance, 0)
    instance.save()
    assert instance.get_concurrency_version() > 0
    assert instance.get_concurrency_version() != copy.get_concurrency_version()



@pytest.mark.django_db(transaction=False)
def test_conflict_with_app_model():
    apply_concurrency_check(Group, 'version', IntegerVersionField)

    instance, __ = Group.objects.get_or_create(name=next(nextgroup))
    instance.save()

    copy = refetch(instance)
    copy.save()

    with pytest.raises(RecordModifiedError):
        instance.save()

