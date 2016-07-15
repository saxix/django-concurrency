# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import site
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils.encoding import force_text

import pytest
from demo.base import SENTINEL, AdminTestCase
from demo.models import ListEditableConcurrentModel
from demo.util import attributes, unique_id

from concurrency.config import (
    CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL, CONCURRENCY_LIST_EDITABLE_POLICY_SILENT
)
from concurrency.exceptions import RecordModifiedError


@pytest.mark.xfail("django.VERSION[:2] == (1, 10)", strict=True)
class TestListEditable(AdminTestCase):
    TARGET = ListEditableConcurrentModel

    def _create_conflict(self, pk):
        u = self.TARGET.objects.get(pk=pk)
        u.username = SENTINEL
        u.save()

    def test_normal_add(self):
        res = self.app.get('/admin/', user='sax')

        res = res.click(self.TARGET._meta.verbose_name_plural)

        res = res.click('Add')
        form = res.form
        form['username'] = 'CHAR'
        res = form.submit().follow()

    def test_normal_update(self):
        self.TARGET.objects.get_or_create(pk=next(unique_id))
        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)
        form = res.forms['changelist-form']
        form['form-0-username'] = 'CHAR'
        res = form.submit('_save').follow()
        self.assertTrue(self.TARGET.objects.filter(username='CHAR').exists())

    def test_concurrency_policy_abort(self):
        id = next(unique_id)
        self.TARGET.objects.get_or_create(pk=id)
        model_admin = site._registry[self.TARGET]
        with attributes((model_admin.__class__, 'list_editable_policy', CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL)):
            res = self.app.get('/admin/', user='sax')
            res = res.click(self.TARGET._meta.verbose_name_plural)
            self._create_conflict(id)

            form = res.forms['changelist-form']
            form['form-0-username'] = 'CHAR'

            with pytest.raises(RecordModifiedError):
                res = form.submit('_save')

            self.assertTrue(self.TARGET.objects.filter(username=SENTINEL).exists())
            self.assertFalse(self.TARGET.objects.filter(username='CHAR').exists())

    def test_concurrency_policy_silent(self):
        id = next(unique_id)
        self.TARGET.objects.get_or_create(pk=id)
        model_admin = site._registry[self.TARGET]
        with attributes((model_admin.__class__, 'list_editable_policy', CONCURRENCY_LIST_EDITABLE_POLICY_SILENT)):
            res = self.app.get('/admin/', user='sax')
            res = res.click(self.TARGET._meta.verbose_name_plural)
            self._create_conflict(id)

            form = res.forms['changelist-form']
            form['form-0-username'] = 'CHAR'
            res = form.submit('_save').follow()
            self.assertTrue(self.TARGET.objects.filter(username=SENTINEL).exists())
            self.assertFalse(self.TARGET.objects.filter(username='CHAR').exists())

    def test_message_user(self):
        id1 = next(unique_id)
        id2 = next(unique_id)
        self.TARGET.objects.get_or_create(pk=id1)
        self.TARGET.objects.get_or_create(pk=id2)
        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)

        self._create_conflict(id1)

        form = res.forms['changelist-form']
        form['form-0-username'] = 'CHAR1'
        form['form-1-username'] = 'CHAR2'
        res = form.submit('_save').follow()

        messages = map(str, list(res.context['messages']))

        self.assertIn('Record with pk `%s` has been modified and was not updated' % id1,
                      messages)
        self.assertIn('1 %s was changed successfully.' % force_text(self.TARGET._meta.verbose_name),
                      messages)

    def test_message_user_no_changes(self):
        id = next(unique_id)
        self.TARGET.objects.get_or_create(pk=id)

        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)

        self._create_conflict(id)

        form = res.forms['changelist-form']
        form['form-0-username'] = 'CHAR1'
        res = form.submit('_save').follow()

        messages = list(map(str, list(res.context['messages'])))

        self.assertIn('Record with pk `%s` has been modified and was not updated' % id, messages)
        self.assertEqual(len(messages), 1)

    def test_log_change(self):
        id = next(unique_id)
        self.TARGET.objects.get_or_create(pk=id)

        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)
        log_filter = dict(user__username='sax',
                          content_type=ContentType.objects.get_for_model(self.TARGET))

        logs = list(LogEntry.objects.filter(**log_filter).values_list('pk', flat=True))

        self._create_conflict(id)

        form = res.forms['changelist-form']
        form['form-0-username'] = 'CHAR1'
        res = form.submit('_save').follow()
        new_logs = LogEntry.objects.filter(**log_filter).exclude(id__in=logs).exists()
        self.assertFalse(new_logs, "LogEntry created even if conflict error")
        transaction.rollback()

# class TestListEditableWithNoActions(TestListEditable):
#     TARGET = NoActionsConcurrentModel
