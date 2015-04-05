import pytest
import django
from concurrency.api import apply_concurrency_check
import concurrency.config
from concurrency.core import _set_version
from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch
from demo.util import (with_all_models, concurrent_model, unique_id,
                       with_std_models)


pytest.mark.django_db(transaction=False)
skip14 = pytest.mark.skipif(django.VERSION[0:2] == (1, 4), reason="skip django 1.4")
skip15 = pytest.mark.skipif(django.VERSION[0:2] == (1, 5), reason="skip django 1.4")


def pytest_generate_tests(metafunc):
    if 'protocol' in metafunc.fixturenames:
        if django.VERSION[1] in [4, 5]:
            metafunc.parametrize("protocol", [1])
        else:
            metafunc.parametrize("protocol", [1, 2])


@with_all_models
@pytest.mark.django_db
def test_standard_save(model_class, protocol, monkeypatch):
    # this test pass if executed alone,
    # produce a Duplicate Key (only django 1.4) if executed with other tests
    monkeypatch.setattr(concurrency.config.conf, 'PROTOCOL', protocol)
    if django.VERSION[:2] == (1, 4):
        model_class.objects.all().delete()
    instance = model_class(username=concurrent_model.__name__)
    instance.save()
    assert instance.get_concurrency_version() > 0


@pytest.mark.django_db(transaction=False)
@with_std_models
def test_conflict(model_class, protocol, monkeypatch):
    monkeypatch.setattr(concurrency.config.conf, 'PROTOCOL', protocol)

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

@skip14
@with_std_models
@pytest.mark.django_db(transaction=False)
def test_update_fields(model_class, protocol, monkeypatch):
    """
    Calling save with update_fields not containing version doesn't update
    the version.
    """
    monkeypatch.setattr(concurrency.config.conf, 'PROTOCOL', protocol)

    instance = model_class.objects.create(username='abc')
    copy = refetch(instance)

    # do not update version
    instance.save(update_fields=['username'])

    # copy can be saved
    copy.username = 'def'
    copy.save()
    assert refetch(instance).username, 'def'
    assert refetch(instance).version == copy.version


@skip14
@with_std_models
@pytest.mark.django_db(transaction=False)
def test_update_fields_still_checks(model_class, protocol, monkeypatch):
    """
    Excluding the VersionField from update_fields should still check
    for conflicts.
    """
    monkeypatch.setattr(concurrency.config.conf, 'PROTOCOL', protocol)
    instance = model_class.objects.create(username='abc')
    copy = refetch(instance)
    instance.save()
    copy.name = 'def'

    with pytest.raises(RecordModifiedError):
        copy.save(update_fields=['username'])
