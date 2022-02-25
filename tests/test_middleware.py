import mock
from demo.base import AdminTestCase
from demo.models import SimpleConcurrentModel
from demo.util import DELETE_ATTRIBUTE, attributes, unique_id
from django.conf import settings
from django.contrib.admin.sites import site
from django.http import HttpRequest
from django.test.utils import override_settings
from django.urls import reverse

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


class ConcurrencyMiddlewareTest1(AdminTestCase):
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


class ConcurrencyMiddlewareTest2(AdminTestCase):
    @property
    def settings_middleware(self):
        return getattr(settings, self.middleware_setting_name) + ['concurrency.middleware.ConcurrencyMiddleware']

    @settings_middleware.setter
    def settings_middleware(self, value):
        setattr(settings, self.middleware_setting_name, value)

    def test_in_admin(self):
        id = next(unique_id)
        model_admin = site._registry[SimpleConcurrentModel]

        with attributes((model_admin.__class__, 'list_editable_policy', CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL),
                        (ConcurrentModelAdmin, 'form', DELETE_ATTRIBUTE)):
            saved, __ = SimpleConcurrentModel.objects.get_or_create(pk=id)

            url = reverse('admin:demo_simpleconcurrentmodel_change', args=[saved.pk])
            res = self.app.get(url, user=self.user.username)
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
