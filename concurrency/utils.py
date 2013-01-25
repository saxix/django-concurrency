# -*- coding: utf-8 -*-
import logging
from django.db.models.fields.related import ForeignKey
from django.forms import model_to_dict

from django.utils.translation import gettext as _
import time
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
        assert get_revision_of_object(target) == get_revision_of_object(
            target_copy), "got same row with different version"
        target.save()
        self.assertRaises(RecordModifiedError, target_copy.save)

    def test_concurrency_safety(self):
        target = self.concurrency_model()
        version = get_revision_of_object(target)
        assert bool(version) is False, "version is not null %s" % v
