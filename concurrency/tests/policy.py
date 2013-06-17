# -*- coding: utf-8 -*-
from mock import Mock
from concurrency.config import CONCURRENCY_POLICY_CALLBACK, CONCURRENCY_POLICY_RAISE
from concurrency.exceptions import RecordModifiedError
from concurrency.tests.models import TestModel0
from concurrency.tests.base import AdminTestCase


class TestPolicy(AdminTestCase):

    def test_policy_callback(self):
        callback = Mock()

        with self.settings(CONCURRENCY_POLICY=CONCURRENCY_POLICY_CALLBACK,
                           CONCURRENCY_CALLBACK=callback):
            obj1, __ = TestModel0.objects.get_or_create(username='123')
            obj2 = TestModel0.objects.get(username='123')

            obj2.save()
            self.assertEqual(callback.call_count, 0)

            obj1.save()
            self.assertEqual(callback.call_count, 1)

    def test_policy_raise(self):
        with self.settings(CONCURRENCY_POLICY=CONCURRENCY_POLICY_RAISE):

            obj1, __ = TestModel0.objects.get_or_create(username='123')
            obj2 = TestModel0.objects.get(username='123')
            obj2.save()
            self.assertRaises(RecordModifiedError, obj1.save)
