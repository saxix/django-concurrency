from concurrency.utils import ConcurrencyTestMixin
from concurrency.tests.models import TestModelWithCustomRevisionMetaInfo
from django.test import TestCase


class TestCustomConcurrencyMeta(ConcurrencyTestMixin, TestCase):
    concurrency_model = TestModelWithCustomRevisionMetaInfo
    concurrency_kwargs = {'username': 'test'}

    def setUp(self):
        super(TestCustomConcurrencyMeta, self).setUp()
        self.TARGET = self._get_concurrency_target()

    def test_enabled(self):
        assert not self.TARGET._concurrencymeta.enabled

    def test_sanity_check(self):
        assert not self.TARGET._concurrencymeta.sanity_check

    def test_concurrency_conflict(self):
        import concurrency.api as api
        target = self._get_concurrency_target()
        target_copy = self._get_concurrency_target()
        v1 = api.get_revision_of_object(target)
        v2 = api.get_revision_of_object(target_copy)
        assert v1 == v2, "got same row with different version (%s/%s)" % (v1, v2)
        target.save()
        assert target.pk is not None  # sanity check
        assert api.get_revision_of_object(target) != api.get_revision_of_object(target_copy)
