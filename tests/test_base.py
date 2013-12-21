import pytest
from concurrency.exceptions import RecordModifiedError
from tests.util import refetch, text, with_all_models


@pytest.mark.django_db
@with_all_models
def test_standard_save(model_class):
    instance = model_class(username=text(10))
    instance.save()
    assert instance.get_concurrency_version() > 0


@pytest.mark.django_db
@with_all_models
def test_conflict(model_class):
    instance = model_class(username=text(10))
    instance.save()
    copy = refetch(instance)
    copy.save()
    with pytest.raises(RecordModifiedError):
        instance.save()
    assert copy.get_concurrency_version() > instance.get_concurrency_version()
