# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.admin.sites import site
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test.utils import override_settings

import mock
import pytest
from demo.base import AdminTestCase
from demo.models import SimpleConcurrentModel
from demo.util import DELETE_ATTRIBUTE, attributes, unique_id

from concurrency.admin import ConcurrentModelAdmin
from concurrency.config import CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL
from concurrency.exceptions import RecordModifiedError
from concurrency.middleware import ConcurrencyMiddleware


def _get_request(path):
    request = HttpRequest()
    request.META = {
        'SERVER_NAME': 'testserver',
        'SERVER_PORT': 80,
    }
    request.path = request.path_info = "/middleware/%s" % path
    return request


def test_middleware():
    handler = mock.Mock(status_code=409)
    type(handler.return_value).status_code = mock.PropertyMock(return_value=409)

    with override_settings(CONCURRENCY_HANDLER409=handler):
        request = _get_request('needsquoting#')
        r = ConcurrencyMiddleware().process_exception(request, RecordModifiedError(target=SimpleConcurrentModel()))
    assert r.status_code == 409


class ConcurrencyMiddlewareTest(AdminTestCase):
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
        id = next(unique_id)
        m, __ = SimpleConcurrentModel.objects.get_or_create(pk=id)
        copy = SimpleConcurrentModel.objects.get(pk=m.pk)
        copy.save()
        request = self._get_request('/')
        r = ConcurrencyMiddleware().process_exception(request, RecordModifiedError(target=m))
        self.assertEqual(r.status_code, 409)

    @pytest.mark.xfail("django.VERSION[:2] == (1, 10)", strict=True)
    def test_in_admin(self):
        id = next(unique_id)

        middlewares = list(settings.MIDDLEWARE_CLASSES) + ['concurrency.middleware.ConcurrencyMiddleware']
        model_admin = site._registry[SimpleConcurrentModel]

        with attributes((model_admin.__class__, 'list_editable_policy', CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL),
                        (ConcurrentModelAdmin, 'form', DELETE_ATTRIBUTE)):

            with self.settings(MIDDLEWARE_CLASSES=middlewares):

                saved, __ = SimpleConcurrentModel.objects.get_or_create(pk=id)

                url = reverse('admin:demo_simpleconcurrentmodel_change', args=[saved.pk])
                res = self.app.get(url, user='sax')
                form = res.form

                saved.save()  # create conflict here

                res = form.submit(expect_errors=True)

                self.assertEqual(res.status_code, 409)

                target = res.context['target']
                self.assertIn('target', res.context)
                self.assertIn('saved', res.context)

                self.assertEqual(res.context['target'].version, target.version)
                self.assertEqual(res.context['saved'].version, saved.version)
                self.assertEqual(res.context['request_path'], url)

#
# class TestFullStack(DjangoAdminTestCase):
#     MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware',
#                           'django.contrib.sessions.middleware.SessionMiddleware',
#                           'django.contrib.auth.middleware.AuthenticationMiddleware',
#                           'django.contrib.messages.middleware.MessageMiddleware',
#                           'concurrency.middleware.ConcurrencyMiddleware',)
#
#     @mock.patch('django.core.signals.got_request_exception.send', mock.Mock())
#     def test_stack(self):
#         admin_register(TestModel0, ModelAdmin)
#
#         with self.settings(MIDDLEWARE_CLASSES=self.MIDDLEWARE_CLASSES):
#             m, __ = TestModel0.objects.get_or_create(username="New", last_name="1")
#             copy = TestModel0.objects.get(pk=m.pk)
#             assert copy.version == m.version
#             print 111111111111, m.version
#             url = reverse('admin:concurrency_testmodel0_change', args=[m.pk])
#             data = {'username': 'new_username',
#                     'last_name': None,
#                     'version': VersionFieldSigner().sign(m.version),
#                     'char_field': None,
#                     '_continue': 1,
#                     'date_field': '2010-09-01'}
#             copy.save()
#             assert copy.version > m.version
#
#             r = self.client.post(url, data, follow=True)
#             self.assertEqual(r.status_code, 409)
#             self.assertIn('target', r.context)
#             self.assertIn('saved', r.context)
#             self.assertEqual(r.context['saved'].version, copy.version)
#             self.assertEqual(r.context['target'].version, m.version)
#             self.assertEqual(r.context['request_path'], url)
