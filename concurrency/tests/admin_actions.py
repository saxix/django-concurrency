# -*- coding: utf-8 -*-
from concurrency.tests.base import AdminTestCase
from concurrency.tests.models import ConcurrentModel


class TestAdminActions(AdminTestCase):

    def test_dummy_action(self):
        res = self.app.get('/admin/', user='sax')
        res = res.click('ConcurrentModels')
        assert 'ConcurrentModel #1' in res  # sanity check
        # update record to create conflict
        u = ConcurrentModel.objects.get(pk=1)
        u.dummy_char = '**concurrent_update**'
        u.save()

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
        res = res.click('ConcurrentModels')
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
        res = res.click('ConcurrentModels')
        assert 'ConcurrentModel #1' in res  # sanity check
        # update record to create conflict
        u = ConcurrentModel.objects.get(pk=1)
        u.dummy_char = 'charfield'
        u.save()

        form = res.forms['changelist-form']
        form['action'].value = 'delete_selected'
        sel = form.get('_selected_action', index=0)
        sel.checked = True
        res = form.submit().follow()
        self.assertIn('One or more record were updated', res)
