import operator
import re
from functools import reduce

import django
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.core.checks import Error
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import transaction
from django.db.models import Q
from django.forms import CheckboxInput
from django.forms.formsets import (
    INITIAL_FORM_COUNT,
    MAX_NUM_FORM_COUNT,
    TOTAL_FORM_COUNT,
    ManagementForm,
)
from django.forms.models import BaseModelFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_str
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from concurrency import core, forms
from concurrency.api import get_revision_of_object
from concurrency.compat import concurrency_param_name
from concurrency.config import CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL, conf
from concurrency.exceptions import RecordModifiedError
from concurrency.forms import ConcurrentForm, VersionWidget
from concurrency.utils import flatten

ALL = object()


class ConcurrencyActionMixin:
    check_concurrent_action = True

    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        """
        if self.check_concurrent_action:
            attrs = {
                "class": "action-select",
                "aria-label": format_html(_("Select this object for an action - {}"), obj),
            }
            checkbox = CheckboxInput(attrs, lambda value: False)
            pk = force_str(f"{obj.pk},{get_revision_of_object(obj)}")
            return checkbox.render(helpers.ACTION_CHECKBOX_NAME, pk)

            # return helpers.checkbox.render(helpers.ACTION_CHECKBOX_NAME,
            #                                force_str("%s,%s" % (obj.pk, get_revision_of_object(obj))))
        # pragma: no cover
        return super().action_checkbox(obj)

    action_checkbox.short_description = mark_safe('<input type="checkbox" id="action-toggle" />')
    action_checkbox.allow_tags = True

    def get_confirmation_template(self) -> str:
        return "concurrency/delete_selected_confirmation.html"

    def response_action(self, request, queryset):  # noqa
        """
        Handle an admin action. This is called if a request is POSTed to the
        changelist; it returns an HttpResponse if the action was handled, and
        None otherwise.
        """
        # There can be multiple action forms on the page (at the top
        # and bottom of the change list, for example). Get the action
        # whose button was pushed.
        try:
            action_index = int(request.POST.get("index", 0))
        except ValueError:  # pragma: no cover
            action_index = 0

        # Construct the action form.
        data = request.POST.copy()
        data.pop(helpers.ACTION_CHECKBOX_NAME, None)
        data.pop("index", None)

        # Use the action whose button was pushed
        try:
            data.update({"action": data.getlist("action")[action_index]})
        except IndexError:  # pragma: no cover
            # If we didn't get an action from the chosen form that's invalid
            # POST data, so by deleting action it'll fail the validation check
            # below. So no need to do anything here
            pass

        action_form = self.action_form(data, auto_id=None)
        action_form.fields["action"].choices = self.get_action_choices(request)

        # If the form's valid we can handle the action.
        if action_form.is_valid():
            action = action_form.cleaned_data["action"]
            func, _name, _description = self.get_actions(request)[action]

            # Get the list of selected PKs. If nothing's selected, we can't
            # perform an action on it, so bail.
            if action_form.cleaned_data["select_across"]:
                selected = ALL
            else:
                selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

            if not selected:
                return None

            revision_field = self.model._concurrencymeta.field

            if self.check_concurrent_action:
                self.delete_selected_confirmation_template = self.get_confirmation_template()

                # If select_across we have to avoid the use of concurrency
                if selected is not ALL:
                    filters = []
                    for x in selected:
                        try:
                            pk, version = x.split(",")
                        except ValueError:  # pragma: no cover
                            msg = (
                                "`ConcurrencyActionMixin` error."
                                "A tuple with `primary_key, version_number` "
                                f"expected:  `{x}` found"
                            )
                            raise ImproperlyConfigured(msg)
                        filters.append(Q(**{"pk": pk, revision_field.attname: version}))

                    queryset = queryset.filter(reduce(operator.or_, filters))
                    if len(selected) != queryset.count():
                        messages.error(
                            request,
                            "One or more record were updated. (Probably by other user) The execution was aborted.",
                        )
                        return HttpResponseRedirect(".")
                else:
                    messages.warning(
                        request,
                        "Selecting all records, you will avoid the concurrency check",
                    )

            response = func(self, request, queryset)

            # Actions may return an HttpResponse, which will be used as the
            # response from the POST. If not, we'll be a good little HTTP
            # citizen and redirect back to the changelist page.
            if isinstance(response, HttpResponse):
                return response
            return HttpResponseRedirect(".")


class ConcurrentManagementForm(ManagementForm):
    def __init__(self, *args, **kwargs) -> None:
        self._versions = kwargs.pop("versions", [])
        super().__init__(*args, **kwargs)

    def _get_concurrency_fields(self):
        v = []
        for pk, version in self._versions:
            v.append(f'<input type="hidden" name="{concurrency_param_name}_{pk}" value="{version}">')
        return mark_safe("".join(v))

    def render(self, template_name=None, context=None, renderer=None):
        out = super().render(template_name, context, renderer)
        return out + self._get_concurrency_fields()

    def __str__(self) -> str:
        if django.VERSION[:2] >= (4, 0):
            return self.render()
        return super().__str__()

    __html__ = __str__

    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        ret = super()._html_output(normal_row, error_row, row_ender, help_text_html, errors_on_separate_row)
        return mark_safe(f"{ret}{self._get_concurrency_fields()}")


class ConcurrentBaseModelFormSet(BaseModelFormSet):
    def _management_form(self):
        """Returns the ManagementForm instance for this FormSet."""
        if self.is_bound:
            form = ConcurrentManagementForm(self.data, auto_id=self.auto_id, prefix=self.prefix)
            if not form.is_valid():
                raise ValidationError("ManagementForm data is missing or has been tampered with")
        else:
            form = ConcurrentManagementForm(
                auto_id=self.auto_id,
                prefix=self.prefix,
                initial={
                    TOTAL_FORM_COUNT: self.total_form_count(),
                    INITIAL_FORM_COUNT: self.initial_form_count(),
                    MAX_NUM_FORM_COUNT: self.max_num,
                },
                versions=[(form.instance.pk, get_revision_of_object(form.instance)) for form in self.initial_forms],
            )
        return form

    management_form = property(_management_form)


class ConcurrencyListEditableMixin:
    list_editable_policy = conf.POLICY

    def get_changelist_formset(self, request, **kwargs):
        kwargs["formset"] = ConcurrentBaseModelFormSet
        return super().get_changelist_formset(request, **kwargs)

    def _add_conflict(self, request, obj) -> None:
        if hasattr(request, "_concurrency_list_editable_errors"):
            request._concurrency_list_editable_errors.append(obj.pk)
        else:
            request._concurrency_list_editable_errors = [obj.pk]

    def _get_conflicts(self, request):
        if hasattr(request, "_concurrency_list_editable_errors"):
            return request._concurrency_list_editable_errors
        return []

    @transaction.atomic()
    def save_model(self, request, obj, form, change) -> None:
        try:
            if change:
                version = request.POST.get(f"{concurrency_param_name}_{obj.pk}", None)
                if version:
                    core._set_version(obj, version)
            super().save_model(request, obj, form, change)
        except RecordModifiedError:
            self._add_conflict(request, obj)
            # If policy is set to 'silent' the user will be informed using message_user
            # raise Exception if not silent.
            # NOTE:
            # list_editable_policy MUST have the LIST_EDITABLE_POLICY_ABORT_ALL
            #   set to work properly
            if self.list_editable_policy == CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL:
                raise

    def log_change(self, request, object, message):
        if object.pk in self._get_conflicts(request):
            return None
        return super().log_change(request, object, message)

    def log_deletion(self, request, object, object_repr):
        if object.pk in self._get_conflicts(request):
            return None
        return super().log_deletion(request, object, object_repr)

    def message_user(self, request, message, *args, **kwargs):
        # This is ugly but we do not want to touch the changelist_view() code.

        opts = self.model._meta
        conflicts = self._get_conflicts(request)
        if conflicts:
            names = force_str(opts.verbose_name), force_str(opts.verbose_name_plural)
            pattern = r"(?P<num>\d+) ({}|{})".format(*names)
            rex = re.compile(pattern)
            m = rex.match(message)
            concurrency_errros = len(conflicts)
            if m:
                updated_record = int(m.group("num")) - concurrency_errros

                ids = ",".join(map(str, conflicts))
                messages.error(
                    request,
                    ngettext(
                        "Record with pk `{0}` has been modified and was not updated",
                        "Records `{0}` have been modified and were not updated",
                        concurrency_errros,
                    ).format(ids),
                )
                name = force_str(opts.verbose_name) if updated_record == 1 else force_str(opts.verbose_name_plural)

                message = None
                if updated_record > 0:
                    message = ngettext(
                        "%(count)s %(name)s was changed successfully.",
                        "%(count)s %(name)s were changed successfully.",
                        updated_record,
                    ) % {"count": updated_record, "name": name}

        return super().message_user(request, message, *args, **kwargs)


class ConcurrentModelAdmin(ConcurrencyActionMixin, ConcurrencyListEditableMixin, admin.ModelAdmin):
    form = ConcurrentForm
    formfield_overrides = {forms.VersionField: {"widget": VersionWidget}}

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        if self.fields:
            version_field = self.model._concurrencymeta.field
            if version_field.name not in self.fields:
                errors.append(
                    Error(
                        f"Missed version field in {self} fields definition",
                        hint=f"Please add '{version_field.name}' to the 'fields' attribute",
                        obj=None,
                        id="concurrency.A001",
                    )
                )
        if self.fieldsets:
            version_field = self.model._concurrencymeta.field
            fields = flatten([v["fields"] for k, v in self.fieldsets])

            if version_field.name not in fields:
                errors.append(
                    Error(
                        f"Missed version field in {self} fieldsets definition",
                        hint=f"Please add '{version_field.name}' to the 'fieldsets' attribute",
                        obj=None,
                        id="concurrency.A002",
                    )
                )
        return errors
