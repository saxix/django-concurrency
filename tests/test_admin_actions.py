import pytest
from demo.base import SENTINEL, AdminTestCase
from demo.models import SimpleConcurrentModel
from demo.util import unique_id
from django.urls import reverse


class TestAdminActions(AdminTestCase):
    def _create_conflict(self, pk):
        u = SimpleConcurrentModel.objects.get(pk=pk)
        u.username = SENTINEL
        u.save()

    def test_dummy_action(self):
        pk = next(unique_id)
        SimpleConcurrentModel.objects.get_or_create(pk=pk)
        res = self.app.get("/admin/", user="sax")

        res = res.click("^SimpleConcurrentModels")
        assert "SimpleConcurrentModel #%s" % pk in res  # sanity check

        self._create_conflict(pk)

        form = res.forms["changelist-form"]
        form["action"].value = "dummy_action"
        sel = form.get("_selected_action", index=0)
        sel.checked = True
        res = form.submit().follow()

        assert "SimpleConcurrentModel #%s" % pk in res
        assert "**concurrent_update**" in res
        assert "**action_update**" not in res

    def test_dummy_action_select_across(self):
        pk = next(unique_id)
        SimpleConcurrentModel.objects.get_or_create(pk=pk)
        res = self.app.get("/admin/", user="sax")

        res = res.click("^SimpleConcurrentModels")
        assert "SimpleConcurrentModel #%s" % pk in res  # sanity check

        self._create_conflict(pk)

        form = res.forms["changelist-form"]
        form["action"].value = "dummy_action"
        form["select_across"] = "True"
        sel = form.get("_selected_action", index=0)  # needed
        sel.checked = True  # needed
        res = form.submit()
        res = res.follow()

        assert "Selecting all records, you will avoid the concurrency check" in res

    def test_delete_allowed_if_no_updates(self):
        pk = next(unique_id)
        SimpleConcurrentModel.objects.get_or_create(pk=pk)
        res = self.app.get("/admin/", user="sax")
        res = res.click("^SimpleConcurrentModels")
        assert "SimpleConcurrentModel #%s" % pk in res  # sanity check

        form = res.forms["changelist-form"]
        form["action"].value = "delete_selected"
        sel = form.get("_selected_action", index=0)
        sel.checked = True

        res = form.submit()

        assert "Are you sure" in res
        assert "SimpleConcurrentModel #%s" % pk in res
        res = res.forms[0].submit()
        assert "SimpleConcurrentModel #%s" % pk not in res

    def test_delete_not_allowed_if_updates(self):
        pk = next(unique_id)

        SimpleConcurrentModel.objects.get_or_create(pk=pk)
        res = self.app.get("/admin/", user="sax")

        res = res.click("^SimpleConcurrentModels")
        assert "SimpleConcurrentModel #%s" % pk in res  # sanity check

        self._create_conflict(pk)

        form = res.forms["changelist-form"]
        form["action"].value = "delete_selected"
        sel = form.get("_selected_action", index=0)
        sel.checked = True
        res = form.submit().follow()
        assert "One or more record were updated" in res

    @pytest.mark.django_db
    def test_deleteaction(self):
        pk = next(unique_id)

        SimpleConcurrentModel.objects.get_or_create(pk=pk)
        response = self.app.get(reverse("admin:demo_simpleconcurrentmodel_changelist"), user="sax")
        form = response.forms["changelist-form"]
        form.get("_selected_action", index=0).checked = True
        form["action"] = "delete_selected"
        response = form.submit()
        expected = "All of the following objects and their related items will be deleted"
        assert expected in response
        form = response.forms[1] if len(response.forms) > 1 else response.form  # dj41
        response = form.submit().follow()
        assert response.status_code == 200
