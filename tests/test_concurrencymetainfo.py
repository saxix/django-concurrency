from django.test import TransactionTestCase

from demo.models import ConcurrencyDisabledModel, SimpleConcurrentModel

from concurrency.exceptions import RecordModifiedError


class TestCustomConcurrencyMeta(TransactionTestCase):
    concurrency_model = ConcurrencyDisabledModel
    concurrency_kwargs = {'username': 'test'}

    def setUp(self):
        super(TestCustomConcurrencyMeta, self).setUp()
        self.TARGET = self._get_concurrency_target()

    def _get_concurrency_target(self, **kwargs):
        # WARNING this method must be idempotent. ie must returns
        # always a fresh copy of the record
        args = dict(self.concurrency_kwargs)
        args.update(kwargs)
        return self.concurrency_model.objects.get_or_create(**args)[0]

    def test_enabled(self):
        assert not self.TARGET._concurrencymeta.enabled

    def test_meta_inheritance(self):
        # TestModelWithCustomOptions extends ConcurrentModel
        # but we disabled concurrency only in TestModelWithCustomOptions
        import concurrency.api as api
        concurrency_enabled1 = SimpleConcurrentModel.objects.get_or_create(**{'username': 'test'})[0]
        concurrency_enabled2 = SimpleConcurrentModel.objects.get_or_create(**{'username': 'test'})[0]
        v1 = api.get_revision_of_object(concurrency_enabled1)
        v2 = api.get_revision_of_object(concurrency_enabled2)
        assert v1 == v2, "got same row with different version (%s/%s)" % (v1, v2)
        concurrency_enabled1.save()
        assert concurrency_enabled1.pk is not None  # sanity check
        self.assertRaises(RecordModifiedError, concurrency_enabled2.save)

        concurrency_disabled1 = ConcurrencyDisabledModel.objects.get_or_create(**{'username': 'test'})[0]
        concurrency_disabled2 = ConcurrencyDisabledModel.objects.get_or_create(**{'username': 'test'})[0]
        v1 = api.get_revision_of_object(concurrency_disabled1)
        v2 = api.get_revision_of_object(concurrency_disabled2)
        assert v1 == v2, "got same row with different version (%s/%s)" % (v1, v2)
        concurrency_disabled1.save()
        assert concurrency_disabled1.pk is not None  # sanity check
        v1 = api.get_revision_of_object(concurrency_disabled1)
        v2 = api.get_revision_of_object(concurrency_disabled2)
        assert v1 != v2
