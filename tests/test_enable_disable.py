import pytest
from demo.models import AutoIncConcurrentModel, SimpleConcurrentModel
from demo.util import nextname
from django.contrib.auth.models import User
from django.test.utils import override_settings

from concurrency.api import concurrency_disable_increment, disable_concurrency
from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch


@pytest.mark.django_db(transaction=False)
def test_disable_concurrency_settings(settings):
    with override_settings(CONCURRENCY_ENABLED=False):
        instance1 = SimpleConcurrentModel(username=next(nextname))
        instance1.save()
        refetch(instance1).save()


@pytest.mark.django_db(transaction=False)
def test_disable_concurrency_global():
    instance1 = SimpleConcurrentModel(username=next(nextname))
    instance2 = AutoIncConcurrentModel(username=next(nextname))
    instance1.save()
    instance2.save()
    refetch(instance1).save()
    refetch(instance2).save()
    with disable_concurrency():
        instance1.save()
        instance2.save()

    copy2 = refetch(instance2)
    refetch(instance2).save()
    with pytest.raises(RecordModifiedError):
        copy2.save()


@pytest.mark.django_db(transaction=False)
def test_disable_concurrency_not_managed():
    u = User(username='u1')
    with disable_concurrency(u):
        u.save()


@pytest.mark.django_db(transaction=False)
def test_disable_concurrency_decorator():

    @disable_concurrency(SimpleConcurrentModel)
    def test1():
        instance = SimpleConcurrentModel(username=next(nextname))
        instance.save()
        copy = refetch(instance)
        copy.save()
        instance.save()
    test1()


@pytest.mark.django_db(transaction=False)
def test_disable_concurrency_class(model_class=SimpleConcurrentModel):
    instance = model_class(username=next(nextname))
    instance.save()
    copy = refetch(instance)
    copy.save()
    with disable_concurrency(SimpleConcurrentModel):
        instance.save()


@pytest.mark.django_db(transaction=False)
def test_disable_concurrency_instance(model_class=SimpleConcurrentModel):
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
def test_concurrency_disable_increment():
    instance1 = AutoIncConcurrentModel(username=next(nextname))
    assert instance1.version == 0
    instance1.save()
    assert instance1.version == 1
    with concurrency_disable_increment(instance1):
        instance1.save()
        instance1.save()
        assert instance1.version == 1
    instance1.save()
    assert instance1.version == 2


@pytest.mark.django_db(transaction=False)
def test_concurrency_disable_increment_on_class():
    instance1 = AutoIncConcurrentModel(username=next(nextname))
    assert instance1.version == 0
    instance1.save()
    assert instance1.version == 1
    with concurrency_disable_increment(AutoIncConcurrentModel):
        instance1.save()
        instance1.save()
        assert instance1.version == 1
    instance1.save()
    assert instance1.version == 2


@pytest.mark.django_db(transaction=False)
def test_concurrency_disable_increment_as_decorator():
    instance1 = AutoIncConcurrentModel(username=next(nextname))

    @concurrency_disable_increment(instance1)
    def test():
        assert instance1.version == 0
        instance1.save()
        assert instance1.version == 1
        instance1.save()
        instance1.save()
        assert instance1.version == 1

    test()
    instance1.save()
    assert instance1.version == 2
