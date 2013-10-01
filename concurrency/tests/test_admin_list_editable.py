# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text

from concurrency.tests.base import AdminTestCase, SENTINEL
from concurrency.tests.models import ListEditableConcurrentModel, NoActionsConcurrentModel


class TestListEditable(AdminTestCase):
    TARGET = ListEditableConcurrentModel

    def _create_conflict(self, pk):
        u = self.TARGET.objects.get(pk=pk)
        u.dummy_char = SENTINEL
        u.save()

    def test_normal_add(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)
        res = res.click('Add')
        form = res.form
        form['dummy_char'] = 'CHAR'
        res = form.submit().follow()

    def test_normal_update(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)
        form = res.forms['changelist-form']
        form['form-0-dummy_char'] = 'CHAR'
        res = form.submit('_save').follow()
        self.assertTrue(self.TARGET.objects.filter(dummy_char='CHAR').exists())

    def test_concurrency(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)

        self._create_conflict(1)

        form = res.forms['changelist-form']
        form['form-0-dummy_char'] = 'CHAR'
        res = form.submit('_save').follow()
        self.assertTrue(self.TARGET.objects.filter(dummy_char=SENTINEL).exists())
        self.assertFalse(self.TARGET.objects.filter(dummy_char='CHAR').exists())

    def test_message_user(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)

        self._create_conflict(1)

        form = res.forms['changelist-form']
        form['form-0-dummy_char'] = 'CHAR1'
        form['form-1-dummy_char'] = 'CHAR2'
        res = form.submit('_save').follow()

        messages = map(str, list(res.context['messages']))

        self.assertIn('Record with pk `1` has been modified and was not updated',
                      messages)
        self.assertIn('1 %s was changed successfully.' % force_text(self.TARGET._meta.verbose_name),
                      messages)

    def test_message_user_no_changes(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)

        self._create_conflict(1)

        form = res.forms['changelist-form']
        form['form-0-dummy_char'] = 'CHAR1'
        res = form.submit('_save').follow()

        messages = list(map(str, list(res.context['messages'])))

        self.assertIn('No %s were changed due conflict errors' % force_text(self.TARGET._meta.verbose_name),
                      messages)
        self.assertEqual(len(messages), 1)

    def test_log_change(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click(self.TARGET._meta.verbose_name_plural)
        log_filter = dict(user__username='sax',
                          content_type=ContentType.objects.get_for_model(self.TARGET))

        logs = list(LogEntry.objects.filter(**log_filter).values_list('pk', flat=True))

        self._create_conflict(1)

        form = res.forms['changelist-form']
        form['form-0-dummy_char'] = 'CHAR1'
        res = form.submit('_save').follow()
        new_logs = LogEntry.objects.filter(**log_filter).exclude(id__in=logs).exists()
        self.assertFalse(new_logs, "LogEntry created even if conflict error")


class TestListEditableWithNoActions(TestListEditable):
    TARGET = NoActionsConcurrentModel
