# -*- coding: utf-8 -*-
import re
from django.contrib.auth.models import User, Group
from django.utils.encoding import force_text
from concurrency.templatetags.concurrency import identity
from concurrency.tests.base import AdminTestCase
from concurrency.tests.models import ListEditableConcurrentModel
from django.contrib.admin.sites import site
from django.http import QueryDict
from django.test.client import RequestFactory


def get_fake_request(params):
    u, __ = User.objects.get_or_create(username='sax')
    setattr(u, 'is_authenticated()', True)
    setattr(u, 'selected_office', False)

    request = RequestFactory().request()
    request.user = u

    querydict = QueryDict(params)
    request.POST = querydict

    return request


class TestIssue16(AdminTestCase):
    def test_concurrency(self):
        model_admin = site._registry[ListEditableConcurrentModel]

        obj, __ = ListEditableConcurrentModel.objects.get_or_create(pk=1)
        request1 = get_fake_request('pk=1&_concurrency_version_1=1')
        model_admin.save_model(request1, obj, None, True)
        self.assertIn(obj.pk, model_admin._get_conflicts(request1))

        obj, __ = ListEditableConcurrentModel.objects.get_or_create(pk=1)
        request2 = get_fake_request('pk=1&_concurrency_version_1=%s' % obj.version)
        model_admin.save_model(request2, obj, None, True)
        self.assertNotIn(obj.pk, model_admin._get_conflicts(request2))


class TestIssue18(AdminTestCase):

    def test_identity_tag(self):
        obj, __ = ListEditableConcurrentModel.objects.get_or_create(pk=1)
        self.assertTrue(re.match(r"^1,\d+$", identity(obj)))

        g, __ = Group.objects.get_or_create(name='GroupTest')
        self.assertEqual(identity(g), force_text(g.pk))
