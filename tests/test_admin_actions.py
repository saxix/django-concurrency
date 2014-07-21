# -*- coding: utf-8 -*-
from tests.base import AdminTestCase, SENTINEL, skipIfDjangoVersion
from tests.models import SimpleConcurrentModel
from tests.util import unique_id


class TestAdminActions(AdminTestCase):
    def _create_conflict(self, pk):
        u = SimpleConcurrentModel.objects.get(pk=pk)
        u.username = SENTINEL
        u.save()

    def test_dummy_action(self):
        id = next(unique_id)
        SimpleConcurrentModel.objects.get_or_create(pk=id)
        res = self.app.get('/admin/', user='sax')

        res = res.click('^SimpleConcurrentModels')
        assert 'SimpleConcurrentModel #%s' % id in res  # sanity check

        self._create_conflict(id)

        form = res.forms['changelist-form']
        form['action'].value = 'dummy_action'
        sel = form.get('_selected_action', index=0)
        sel.checked = True
        res = form.submit().follow()

        self.assertIn('SimpleConcurrentModel #%s' % id, res)
        self.assertIn('**concurrent_update**', res)
        self.assertNotIn('**action_update**', res)

    @skipIfDjangoVersion((1,7))
    def test_delete_allowed_if_no_updates(self):
        id = next(unique_id)
        SimpleConcurrentModel.objects.get_or_create(pk=id)
        res = self.app.get('/admin/', user='sax')
        res = res.click('^SimpleConcurrentModels')
        assert 'SimpleConcurrentModel #%s' % id in res  # sanity check

        form = res.forms['changelist-form']
        form['action'].value = 'delete_selected'
        sel = form.get('_selected_action', index=0)
        sel.checked = True

        res = form.submit()
        assert 'Are you sure?' in res
        assert 'SimpleConcurrentModel #%s' % id in res
        res = res.form.submit()
        assert 'SimpleConcurrentModel #%s' % id not in res

    def test_delete_not_allowed_if_updates(self):
        id = next(unique_id)

        SimpleConcurrentModel.objects.get_or_create(pk=id)
        res = self.app.get('/admin/', user='sax')
        res = res.click('^SimpleConcurrentModels')
        assert 'SimpleConcurrentModel #%s' % id in res  # sanity check

        self._create_conflict(id)

        form = res.forms['changelist-form']
        form['action'].value = 'delete_selected'
        sel = form.get('_selected_action', index=0)
        sel.checked = True
        res = form.submit().follow()
        self.assertIn('One or more record were updated', res)
