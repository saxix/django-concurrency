# -*- coding: utf-8 -*-
from concurrency.tests.base import AdminTestCase
from concurrency.tests.models import ConcurrentModel

SENTINEL = '**concurrent_update**'


class TestListEditable(AdminTestCase):

    def _concurret_update(self, pk):
        u = ConcurrentModel.objects.get(pk=pk)
        u.dummy_char = SENTINEL
        u.save()

    def test_normal_update(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click('ConcurrentModels')
        form = res.forms['changelist-form']
        form['form-0-dummy_char'] = 'CHAR'
        res = form.submit('_save').follow()
        self.assertTrue(ConcurrentModel.objects.filter(dummy_char='CHAR').exists())

    def test_concurrency(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click('ConcurrentModels')
        self._concurret_update(1)
        form = res.forms['changelist-form']
        form['form-0-dummy_char'] = 'CHAR'
        res = form.submit('_save').follow()
        self.assertTrue(ConcurrentModel.objects.filter(dummy_char=SENTINEL).exists())
        self.assertFalse(ConcurrentModel.objects.filter(dummy_char='CHAR').exists())
