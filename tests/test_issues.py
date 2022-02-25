import re

import pytest
from demo.admin import ActionsModelAdmin, admin_register
from demo.base import AdminTestCase
from demo.models import ListEditableConcurrentModel, SimpleConcurrentModel
from demo.util import attributes, unique_id
from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.http import QueryDict
from django.test import override_settings
from django.test.client import RequestFactory
from django.test.testcases import SimpleTestCase
from django.utils.encoding import force_str

from concurrency.admin import ConcurrentModelAdmin
from concurrency.compat import concurrency_param_name
from concurrency.config import CONCURRENCY_LIST_EDITABLE_POLICY_SILENT
from concurrency.exceptions import RecordModifiedError
from concurrency.forms import ConcurrentForm
from concurrency.templatetags.concurrency import identity
from concurrency.utils import refetch


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

            # post_param = 'form-_concurrency_version' if django.VERSION[:2] >= (4, 0) else '_concurrency_version'

            # request1 = get_fake_request('pk={}&{}_1=2'.format(id, post_param))
            request1 = get_fake_request(f'pk={id}&{concurrency_param_name}_1=2')

            model_admin.save_model(request1, obj, None, True)

            self.assertIn(obj.pk, model_admin._get_conflicts(request1))

            obj = refetch(obj)
            request2 = get_fake_request(f'pk={id}&{concurrency_param_name}_1={obj.version}')
            model_admin.save_model(request2, obj, None, True)
            self.assertNotIn(obj.pk, model_admin._get_conflicts(request2))


class TestIssue18(SimpleTestCase):
    def test_identity_tag(self):
        id = next(unique_id)

        obj = ListEditableConcurrentModel(pk=id)
        self.assertTrue(re.match(r"^%s,\d+$" % id, identity(obj)))

        g = User(username='UserTest', pk=3)
        self.assertEqual(identity(g), force_str(g.pk))


@pytest.mark.django_db()
def test_issue_54():
    with override_settings(CONCURRENCY_VERSION_FIELD_REQUIRED=False):
        m = SimpleConcurrentModel(version=0)
        m.save()
        SimpleConcurrentModel.objects.update(version=0)
        m1 = SimpleConcurrentModel.objects.get(pk=m.pk)
        m2 = SimpleConcurrentModel.objects.get(pk=m.pk)
        assert m1.version == m2.version == 0
        m1.save()
        m2.save()

    with override_settings(CONCURRENCY_VERSION_FIELD_REQUIRED=True):
        m = SimpleConcurrentModel(version=0)
        m.save()
        SimpleConcurrentModel.objects.update(version=0)
        m1 = SimpleConcurrentModel.objects.get(pk=m.pk)
        m2 = SimpleConcurrentModel.objects.get(pk=m.pk)
        assert m1.version == m2.version == 0
        m1.save()

        with pytest.raises(RecordModifiedError):
            m2.save()


@pytest.mark.django_db()
def test_issue_81a(monkeypatch):
    monkeypatch.setattr('demo.admin.ActionsModelAdmin.fields', ('id',))
    with pytest.raises(SystemCheckError) as e:
        call_command('check')
    assert 'concurrency.A001' in str(e.value)


@pytest.mark.django_db()
def test_issue_81b(monkeypatch):
    fieldsets = (
        ('Standard info', {
            'fields': ('id',)
        }),
    )
    monkeypatch.setattr('demo.admin.ActionsModelAdmin.fieldsets', fieldsets)
    with pytest.raises(SystemCheckError) as e:
        call_command('check')
    assert 'concurrency.A002' in str(e.value)
