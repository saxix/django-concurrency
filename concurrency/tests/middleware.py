# -*- coding: utf-8 -*-
from django.http import HttpRequest
from django.test import TestCase
from concurrency.core import RecordModifiedError
from concurrency.middleware import ConcurrencyMiddleware
from concurrency.tests import TestModel0


class ConcurrencyMiddlewareTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_request(self, path):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
        }
        request.path = request.path_info = "/middleware/%s" % path
        return request

    def test_process_exception(self):
        """
        Tests that RecordModifiedError is handled correctly.
        """
        m, __ = TestModel0.objects.get_or_create(username="New", last_name="1")
        copy = TestModel0.objects.get(pk=m.pk)
        copy.save()
        request = self._get_request('/')
        r = ConcurrencyMiddleware().process_exception(request, RecordModifiedError(target=m))
        self.assertEqual(r.status_code, 409)
