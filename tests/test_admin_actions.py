# -*- coding: utf-8 -*-
import django

import pytest
from demo.base import SENTINEL, AdminTestCase
from demo.models import SimpleConcurrentModel
from demo.util import unique_id


@pytest.mark.xfail("django.VERSION[:2] == (1, 10)", strict=True)
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

    def test_dummy_action_select_across(self):
        id = next(unique_id)
        SimpleConcurrentModel.objects.get_or_create(pk=id)
        res = self.app.get('/admin/', user='sax')

        res = res.click('^SimpleConcurrentModels')
        assert 'SimpleConcurrentModel #%s' % id in res  # sanity check

        self._create_conflict(id)

        form = res.forms['changelist-form']
        form['action'].value = 'dummy_action'
        form['select_across'] = 'True'
        sel = form.get('_selected_action', index=0)  # needed
        sel.checked = True  # needed
        res = form.submit()
        res = res.follow()

        self.assertIn('Selecting all records, you will avoid the concurrency check', res)

    # @pytest.mark.skipif(django.VERSION[:2] >= (1, 7), reason="Skip django>=1.9")
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

    # @pytest.mark.skipif(django.VERSION[:2] >= (1, 10), reason="Skip django>=1.10")
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

    @pytest.mark.django_db
    def test_deleteaction(self):
        id = next(unique_id)

        SimpleConcurrentModel.objects.get_or_create(pk=id)
        response = self.app.get(django.core.urlresolvers.reverse('admin:demo_simpleconcurrentmodel_changelist'),
                                user='sax')
        form = response.forms['changelist-form']
        form.get('_selected_action', index=0).checked = True
        form['action'] = 'delete_selected'
        response = form.submit()
        expected = 'All of the following objects and their related items will be deleted'
        assert expected in response
        response = response.form.submit().follow()
        assert response.status_code == 200
