# -*- coding: utf-8 -*-
import logging
from concurrency.core import RecordModifiedError

logger = logging.getLogger('tests.concurrency')
logger.setLevel(logging.DEBUG)


def get_revision_of_object(obj):
    """

    @param obj:
    @return:
    """
    revision_field = obj.RevisionMetaInfo.field
    value = getattr(obj, revision_field.attname)
    return value


class ConcurrencyTestMixin(object):
    """
    Mixin class to test Models that use `VersionField`

    this class offer a simple test scenario. Its purpose is to discover
    some conflict in the `save()` inheritance::

        from concurrency.utils import ConcurrencyTestMixin
        from myproject.models import MyModel

        class MyModelTest(ConcurrencyTestMixin, TestCase):
            concurrency_model = TestModel0
            concurrency_kwargs = {'username': 'test'}

    """

    concurrency_model = None
    concurrency_kwargs = {}

    def _get_concurrency_target(self, **kwargs):
        args = dict(self.concurrency_kwargs)
        args.update(kwargs)
        return self.concurrency_model.objects.get_or_create(**args)[0]

    def test_concurrency_conflict(self):
        target = self._get_concurrency_target()
        target_copy = self._get_concurrency_target()
        v1 = get_revision_of_object(target)
        v2 = get_revision_of_object(target_copy)
        assert v1 == v2, "got same row with different version (%s/%s)" % (v1, v2)
        target.save()
        self.assertRaises(RecordModifiedError, target_copy.save)

    def test_concurrency_safety(self):
        target = self.concurrency_model()
        version = get_revision_of_object(target)
        self.assertFalse(bool(version), "version is not null %s" % version)

    def test_concurrency_management(self):
        target = self.concurrency_model
        self.assertTrue(hasattr(target, 'RevisionMetaInfo'),
                        "%s is not under concurrency management" % self.concurrency_model)
        info = getattr(target, 'RevisionMetaInfo', None)
        revision_field = info.field

        self.assertTrue(revision_field in target._meta.fields,
                        "%s: version field not in meta.fields" % self.concurrency_model)
