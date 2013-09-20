# -*- coding: utf-8 -*-
from concurrency.tests.base import AdminTestCase, SENTINEL
from concurrency.tests.models import ConcurrentModel


class TestAdminActions(AdminTestCase):

    def _create_conflict(self, pk):
        u = ConcurrentModel.objects.get(pk=pk)
        u.dummy_char = SENTINEL
        u.save()

    def test_dummy_action(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click('^ConcurrentModels')
        assert 'ConcurrentModel #1' in res  # sanity check

        self._create_conflict(1)

        form = res.forms['changelist-form']
        form['action'].value = 'dummy_action'
        sel = form.get('_selected_action', index=0)
        sel.checked = True
        res = form.submit().follow()
        self.assertIn('ConcurrentModel #1', res)
        self.assertIn('**concurrent_update**', res)
        self.assertNotIn('**action_update**', res)

    def test_delete_allowed_if_no_updates(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click('^ConcurrentModels')
        assert 'ConcurrentModel #1' in res  # sanity check

        form = res.forms['changelist-form']
        form['action'].value = 'delete_selected'
        sel = form.get('_selected_action', index=0)
        sel.checked = True
        res = form.submit()
        assert 'Are you sure?' in res
        assert 'ConcurrentModel #1' in res
        res = res.form.submit()
        self.assertNotIn('ConcurrentModel #1', res)

    def test_delete_not_allowed_if_updates(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click('^ConcurrentModels')
        assert 'ConcurrentModel #1' in res  # sanity check

        self._create_conflict(1)

        form = res.forms['changelist-form']
        form['action'].value = 'delete_selected'
        sel = form.get('_selected_action', index=0)
        sel.checked = True
        res = form.submit().follow()
        self.assertIn('One or more record were updated', res)
