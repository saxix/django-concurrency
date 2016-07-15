import pytest
from django.test import override_settings

from demo.util import concurrent_model, unique_id, with_all_models, with_std_models

from concurrency.core import _set_version
from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch

pytest.mark.django_db(transaction=False)


@with_all_models
@pytest.mark.django_db
def test_standard_save(model_class):
    instance = model_class(username=concurrent_model.__name__)
    instance.save()
    assert instance.get_concurrency_version() > 0
    instance = refetch(instance)
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


@pytest.mark.django_db(transaction=True)
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


@pytest.mark.django_db(transaction=True)
@with_std_models
def test_conflict_no_version_and_no_skip_flag(model_class):
    """When IGNORE_DEFAULT is disabled, attempting to update a record with a default version number should fail."""
    with override_settings(CONCURRENCY_IGNORE_DEFAULT=False):
        id = next(unique_id)
        instance, __ = model_class.objects.get_or_create(pk=id)
        instance.save()

        copy = refetch(instance)
        copy.version = 0

        with pytest.raises(RecordModifiedError):
            copy.save()


@with_std_models
@pytest.mark.django_db(transaction=False)
def test_update_fields(model_class):
    """
    Calling save with update_fields not containing version doesn't update
    the version.
    """

    instance = model_class.objects.create(username='abc')
    copy = refetch(instance)

    # do not update version
    instance.save(update_fields=['username'])

    # copy can be saved
    copy.username = 'def'
    copy.save()
    assert refetch(instance).username, 'def'
    assert refetch(instance).version == copy.version


@with_std_models
@pytest.mark.django_db(transaction=False)
def test_update_fields_still_checks(model_class):
    """
    Excluding the VersionField from update_fields should still check
    for conflicts.
    """
    instance = model_class.objects.create(username='abc')
    copy = refetch(instance)
    instance.save()
    copy.name = 'def'

    with pytest.raises(RecordModifiedError):
        copy.save(update_fields=['username'])
