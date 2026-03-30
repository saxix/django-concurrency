import logging

import pytest
from demo.models import SimpleConcurrentModel
from django.test import TestCase

import concurrency.fields
from concurrency.utils import ConcurrencyTestMixin, deprecated, fqn

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestConcurrencyTestMixin(ConcurrencyTestMixin, TestCase):
    concurrency_model = SimpleConcurrentModel


def test_fqn():
    with pytest.raises(ValueError, match="Invalid"):
        fqn("str")

    assert fqn(SimpleConcurrentModel) == "demo.models.SimpleConcurrentModel"
    assert fqn(SimpleConcurrentModel()) == "demo.models.SimpleConcurrentModel"
    assert fqn(concurrency.fields) == "concurrency.fields"


def test_deprecated():
    @deprecated()
    def foo1(x):
        return x

    with pytest.warns(DeprecationWarning, match=r"deprecated"):
        assert foo1(12) == 12

    def newfun(x):
        return 0

    @deprecated(newfun, "1.1")
    def foo2(x):
        return x

    with pytest.warns(DeprecationWarning, match=r"deprecated"):
        assert foo2(10) == 0
