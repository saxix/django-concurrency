# -*- coding: utf-8 -*-
import mock
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase
from concurrency.core import RecordModifiedError
from concurrency.forms import VersionFieldSigner
from concurrency.middleware import ConcurrencyMiddleware
from concurrency.tests import TestModel0
from concurrency.tests.contrib_admin import DjangoAdminTestCase


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

    @mock.patch('django.core.signals.got_request_exception.send', mock.Mock())
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
        # self.assertIn('target', r.context)


class CT(DjangoAdminTestCase):
    MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware',
                          'django.contrib.sessions.middleware.SessionMiddleware',
                          'django.contrib.auth.middleware.AuthenticationMiddleware',
                          'concurrency.middleware.ConcurrencyMiddleware',)

    @mock.patch('django.core.signals.got_request_exception.send', mock.Mock())
    def test_stack(self):
        m, __ = TestModel0.objects.get_or_create(username="New", last_name="1")
        copy = TestModel0.objects.get(pk=m.pk)
        url = reverse('admin:concurrency_testmodel0_change', args=[m.pk])

        data = {'username': 'new_username',
                'last_name': None,
                'version': VersionFieldSigner().sign(m.version),
                'char_field': None,
                '_continue': 1,
                'date_field': '2010-09-01'}
        copy.save()
        r = self.client.post(url, data, follow=True)
        self.assertEqual(r.status_code, 409)
        self.assertIn('target', r.context)
        self.assertIn('saved', r.context)
        self.assertEqual(r.context['saved'].version, copy.version)
        self.assertEqual(r.context['target'].version, m.version)
        self.assertEqual(r.context['request_path'], url)
