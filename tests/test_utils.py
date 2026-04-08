import logging

import pytest
from demo.models import SimpleConcurrentModel
from django.test import TestCase

import concurrency.fields
from concurrency.test_utils import ConcurrencyTestMixin
from concurrency.utils import deprecated, flatten, fqn, get_classname, refetch

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


def test_get_classname():
    assert get_classname(SimpleConcurrentModel) == "SimpleConcurrentModel"
    assert get_classname(SimpleConcurrentModel()) == "SimpleConcurrentModel"


@pytest.mark.django_db
def test_refetch():
    m = SimpleConcurrentModel.objects.create(username="test")
    assert refetch(m) == m


def test_flatten():
    assert flatten([1, 2, [3, 4], (5, 6)]) == [1, 2, 3, 4, 5, 6]
    assert flatten([[[1, 2, 3], (42, None)], [4, 5], [6], 7, (8, 9, 10)]) == [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]


def test_concurrency_test_mixin_errors():
    from unittest.mock import MagicMock, patch  # noqa: PLC0415

    class BrokenModel:
        class objects:  # noqa: N801
            @staticmethod
            def get_or_create(**kwargs):
                m = MagicMock()
                m.pk = 1
                return m, False

    mixin = ConcurrencyTestMixin()
    mixin.concurrency_model = BrokenModel

    with patch("concurrency.api.get_revision_of_object", side_effect=[1, 2]):
        with pytest.raises(ValueError, match="Got same row with different version"):
            mixin.test_concurrency_conflict()

    with patch("concurrency.api.get_revision_of_object", return_value=1):
        with patch.object(BrokenModel.objects, "get_or_create") as mock_get:
            m = MagicMock()
            m.pk = None
            mock_get.return_value = (m, False)
            with pytest.raises(ValueError, match="target must be saved"):
                mixin.test_concurrency_conflict()


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
