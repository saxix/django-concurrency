# -*- coding: utf-8 -*-
from concurrency.tests.base import AdminTestCase, SENTINEL
from concurrency.tests.models import ListEditableConcurrentModel, NoActionsConcurrentModel


class TestListEditable(AdminTestCase):
    TARGET = ListEditableConcurrentModel

    def _create_conflict(self, pk):
        u = self.TARGET.objects.get(pk=pk)
        u.dummy_char = SENTINEL
        u.save()

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


class TestListEditableWithNoActions(TestListEditable):
    TARGET = NoActionsConcurrentModel
