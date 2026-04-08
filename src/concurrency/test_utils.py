import logging
import pytest

from concurrency.exceptions import RecordModifiedError

logger = logging.getLogger(__name__)


class ConcurrencyTestMixin:
    """Mixin class to test Models that use `VersionField`.

    this class offer a simple test scenario. Its purpose is to discover
    some conflict in the `save()` inheritance::

        from concurrency.utils import ConcurrencyTestMixin
        from myproject.models import MyModel


        class MyModelTest(ConcurrencyTestMixin, TestCase):
            concurrency_model = TestModel0
            concurrency_kwargs = {"username": "test"}

    """

    concurrency_model = None
    concurrency_kwargs = {}

    def _get_concurrency_target(self, **kwargs):
        # WARNING this method must be idempotent. ie must returns
        # always a fresh copy of the record
        args = dict(self.concurrency_kwargs)
        args.update(kwargs)
        return self.concurrency_model.objects.get_or_create(**args)[0]

    def test_concurrency_conflict(self) -> None:
        from concurrency import api  # noqa: PLC0415

        target = self._get_concurrency_target()
        target_copy = self._get_concurrency_target()
        v1 = api.get_revision_of_object(target)
        v2 = api.get_revision_of_object(target_copy)
        if v1 != v2:
            raise ValueError(f"Got same row with different version ({v1}/{v2})")
        target.save()
        if target.pk is None:
            raise ValueError("target must be saved (pk is None)")

        with pytest.raises(RecordModifiedError):
            target_copy.save()

    def test_concurrency_safety(self) -> None:
        from concurrency import api  # noqa

        target = self.concurrency_model()
        version = api.get_revision_of_object(target)
        assert not bool(version), f"version is not null {version}"  # noqa: S101

    def test_concurrency_management(self) -> None:
        target = self.concurrency_model
        assert hasattr(target, "_concurrencymeta"), f"{self.concurrency_model} is not under concurrency management"  # noqa: S101

        revision_field = target._concurrencymeta.field

        assert revision_field in target._meta.fields, f"{self.concurrency_model}: version field not in meta.fields"  # noqa: S101


class ConcurrencyAdminTestMixin:
    pass
