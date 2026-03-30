import pytest
from demo.base import SENTINEL, AdminTestCase
from demo.models import ListEditableConcurrentModel
from demo.util import attributes, unique_id
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import site
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils.encoding import force_str

from concurrency.compat import concurrency_param_name
from concurrency.config import (
    CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL,
    CONCURRENCY_LIST_EDITABLE_POLICY_SILENT,
)
from concurrency.exceptions import RecordModifiedError


class TestListEditable(AdminTestCase):
    TARGET = ListEditableConcurrentModel

    def _create_conflict(self, pk):
        u = self.TARGET.objects.get(pk=pk)
        u.username = SENTINEL
        u.save()

    def test_normal_add(self):
        res = self.app.get("/admin/", user="sax")
        # file:///admin/demo/listeditableconcurrentmodel/add/
        res = res.click(self.TARGET._meta.verbose_name_plural)
        res = res.click("Add", href=f"/admin/demo/{self.TARGET._meta.model_name}/add/", index=0)
        form = res.forms["listeditableconcurrentmodel_form"]
        form["username"] = "CHAR"
        form.submit().follow()

    def test_normal_update(self):
        self.TARGET.objects.get_or_create(pk=next(unique_id))
        res = self.app.get("/admin/", user="sax")
        res = res.click(self.TARGET._meta.verbose_name_plural)
        form = res.forms["changelist-form"]
        form["form-0-username"] = "CHAR"
        form.submit("_save").follow()
        assert self.TARGET.objects.filter(username="CHAR").exists()

    def test_concurrency_policy_abort(self):
        pk = next(unique_id)
        self.TARGET.objects.get_or_create(pk=pk)
        model_admin = site._registry[self.TARGET]
        with attributes(
            (
                model_admin.__class__,
                "list_editable_policy",
                CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL,
            )
        ):
            res = self.app.get("/admin/", user="sax")
            res = res.click(self.TARGET._meta.verbose_name_plural)
            self._create_conflict(pk)
            form = res.forms["changelist-form"]
            form["form-0-username"] = "CHAR"

            with pytest.raises(RecordModifiedError):
                form.submit("_save")

            assert self.TARGET.objects.filter(username=SENTINEL).exists()
            assert not self.TARGET.objects.filter(username="CHAR").exists()

    def test_concurrency_policy_silent(self):
        pk = next(unique_id)
        self.TARGET.objects.get_or_create(pk=pk)
        model_admin = site._registry[self.TARGET]
        with attributes(
            (
                model_admin.__class__,
                "list_editable_policy",
                CONCURRENCY_LIST_EDITABLE_POLICY_SILENT,
            )
        ):
            res = self.app.get("/admin/", user="sax")
            res = res.click(self.TARGET._meta.verbose_name_plural)
            self._create_conflict(pk)
            form = res.forms["changelist-form"]
            form["form-0-username"] = "CHAR"
            version = int(form[f"{concurrency_param_name}_{pk}"].value)
            form.submit("_save").follow()
            changed = self.TARGET.objects.filter(username=SENTINEL).first()
            assert changed
            assert changed.version > version

    def test_message_user(self):
        id1 = next(unique_id)
        id2 = next(unique_id)
        self.TARGET.objects.get_or_create(pk=id1)
        self.TARGET.objects.get_or_create(pk=id2)
        res = self.app.get("/admin/", user="sax")
        res = res.click(self.TARGET._meta.verbose_name_plural)

        self._create_conflict(id1)

        form = res.forms["changelist-form"]
        form["form-0-username"] = "CHAR1"
        form["form-1-username"] = "CHAR2"
        res = form.submit("_save").follow()

        messages = [str(m) for m in res.context["messages"]]

        assert "Record with pk `%s` has been modified and was not updated" % id1 in messages
        assert "1 %s was changed successfully." % force_str(self.TARGET._meta.verbose_name) in messages

    def test_message_user_no_changes(self):
        pk = next(unique_id)
        self.TARGET.objects.get_or_create(pk=pk)

        res = self.app.get("/admin/", user="sax")
        res = res.click(self.TARGET._meta.verbose_name_plural)

        self._create_conflict(pk)

        form = res.forms["changelist-form"]
        form["form-0-username"] = "CHAR1"
        res = form.submit("_save").follow()

        messages = [str(m) for m in res.context["messages"]]
        assert "Record with pk `%s` has been modified and was not updated" % pk in set(messages)

        assert len(set(messages)) == 1

    def test_log_change(self):
        pk = next(unique_id)
        self.TARGET.objects.get_or_create(pk=pk)

        res = self.app.get("/admin/", user="sax")
        res = res.click(self.TARGET._meta.verbose_name_plural)
        log_filter = {
            "user__username": "sax",
            "content_type": ContentType.objects.get_for_model(self.TARGET),
        }

        logs = list(LogEntry.objects.filter(**log_filter).values_list("pk", flat=True))

        self._create_conflict(pk)

        form = res.forms["changelist-form"]
        form["form-0-username"] = "CHAR1"
        form.submit("_save").follow()
        assert not LogEntry.objects.filter(**log_filter).exclude(id__in=logs).exists()
        transaction.rollback()
