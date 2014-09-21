# -*- coding: utf-8 -*-
import re
from django.contrib.auth.models import User, Group
from django.test.testcases import SimpleTestCase
from django.utils.encoding import force_text
from concurrency.admin import ConcurrentModelAdmin
from concurrency.config import CONCURRENCY_LIST_EDITABLE_POLICY_SILENT
from concurrency.forms import ConcurrentForm
from concurrency.templatetags.concurrency import identity
from django.contrib.admin.sites import site
from django.http import QueryDict
from django.test.client import RequestFactory
from concurrency.utils import refetch
from tests.admin import admin_register, ActionsModelAdmin

from tests.base import AdminTestCase
from tests.models import ListEditableConcurrentModel
from tests.util import unique_id, attributes


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
        id = 1
        admin_register(ListEditableConcurrentModel, ActionsModelAdmin)
        model_admin = site._registry[ListEditableConcurrentModel]
        with attributes((ConcurrentModelAdmin, 'list_editable_policy', CONCURRENCY_LIST_EDITABLE_POLICY_SILENT),
                        (ConcurrentModelAdmin, 'form', ConcurrentForm), ):
            obj, __ = ListEditableConcurrentModel.objects.get_or_create(pk=id)
            request1 = get_fake_request('pk=%s&_concurrency_version_1=2' % id)

            model_admin.save_model(request1, obj, None, True)

            self.assertIn(obj.pk, model_admin._get_conflicts(request1))

            obj = refetch(obj)
            request2 = get_fake_request('pk=%s&_concurrency_version_1=%s' % (id, obj.version))
            model_admin.save_model(request2, obj, None, True)
            self.assertNotIn(obj.pk, model_admin._get_conflicts(request2))


class TestIssue18(SimpleTestCase):
    def test_identity_tag(self):
        id = next(unique_id)

        obj = ListEditableConcurrentModel(pk=id)
        self.assertTrue(re.match(r"^%s,\d+$" % id, identity(obj)))

        g = User(username='UserTest', pk=3)
        self.assertEqual(identity(g), force_text(g.pk))
