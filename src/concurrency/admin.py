# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import operator
import re
from functools import reduce

from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models import Q
from django.forms.formsets import (
    INITIAL_FORM_COUNT, MAX_NUM_FORM_COUNT, TOTAL_FORM_COUNT, ManagementForm
)
from django.forms.models import BaseModelFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext

from concurrency import core, forms
from concurrency.api import get_revision_of_object
from concurrency.config import CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL, conf
from concurrency.exceptions import RecordModifiedError
from concurrency.forms import ConcurrentForm, VersionWidget

ALL = object()


class ConcurrencyActionMixin(object):
    check_concurrent_action = True

    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        """
        if self.check_concurrent_action:
            return helpers.checkbox.render(helpers.ACTION_CHECKBOX_NAME,
                                           force_text("%s,%s" % (obj.pk,
                                                                 get_revision_of_object(obj))))
        else:
            return super(ConcurrencyActionMixin, self).action_checkbox(obj)

    action_checkbox.short_description = mark_safe('<input type="checkbox" id="action-toggle" />')
    action_checkbox.allow_tags = True

    def get_confirmation_template(self):
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
            action_index = int(request.POST.get('index', 0))
        except ValueError:  # pragma: no cover
            action_index = 0

        # Construct the action form.
        data = request.POST.copy()
        data.pop(helpers.ACTION_CHECKBOX_NAME, None)
        data.pop("index", None)

        # Use the action whose button was pushed
        try:
            data.update({'action': data.getlist('action')[action_index]})
        except IndexError:
            # If we didn't get an action from the chosen form that's invalid
            # POST data, so by deleting action it'll fail the validation check
            # below. So no need to do anything here
            pass

        action_form = self.action_form(data, auto_id=None)
        action_form.fields['action'].choices = self.get_action_choices(request)

        # If the form's valid we can handle the action.
        if action_form.is_valid():
            action = action_form.cleaned_data['action']
            func, name, description = self.get_actions(request)[action]

            # Get the list of selected PKs. If nothing's selected, we can't
            # perform an action on it, so bail.
            if action_form.cleaned_data['select_across']:
                selected = ALL
            else:
                selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

            revision_field = self.model._concurrencymeta.field
            if not selected:
                return None

            if self.check_concurrent_action:
                self.delete_selected_confirmation_template = self.get_confirmation_template()

                # If select_across we have to avoid the use of concurrency
                if selected is not ALL:
                    filters = []
                    for x in selected:
                        try:
                            pk, version = x.split(",")
                        except ValueError:
                            raise ImproperlyConfigured('`ConcurrencyActionMixin` error.'
                                                       'A tuple with `primary_key, version_number` '
                                                       'expected:  `%s` found' % x)
                        filters.append(Q(**{'pk': pk,
                                            revision_field.attname: version}))

                    queryset = queryset.filter(reduce(operator.or_, filters))
                    if len(selected) != queryset.count():
                        messages.error(request, 'One or more record were updated. '
                                                '(Probably by other user) '
                                                'The execution was aborted.')
                        return HttpResponseRedirect(".")
                else:
                    messages.warning(request, 'Selecting all records, you will avoid the concurrency check')

            response = func(self, request, queryset)

            # Actions may return an HttpResponse, which will be used as the
            # response from the POST. If not, we'll be a good little HTTP
            # citizen and redirect back to the changelist page.
            if isinstance(response, HttpResponse):
                return response
            else:
                return HttpResponseRedirect(".")


class ConcurrentManagementForm(ManagementForm):
    def __init__(self, *args, **kwargs):
        self._versions = kwargs.pop('versions', [])
        super(ConcurrentManagementForm, self).__init__(*args, **kwargs)

    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        ret = super(ConcurrentManagementForm, self)._html_output(normal_row, error_row, row_ender, help_text_html,
                                                                 errors_on_separate_row)
        v = []
        for pk, version in self._versions:
            v.append('<input type="hidden" name="_concurrency_version_{0}" value="{1}">'.format(pk, version))
        return mark_safe("{0}{1}".format(ret, "".join(v)))


class ConcurrentBaseModelFormSet(BaseModelFormSet):
    def _management_form(self):
        """Returns the ManagementForm instance for this FormSet."""
        if self.is_bound:
            form = ConcurrentManagementForm(self.data, auto_id=self.auto_id,
                                            prefix=self.prefix)
            if not form.is_valid():
                raise ValidationError('ManagementForm data is missing or has been tampered with')
        else:
            form = ConcurrentManagementForm(auto_id=self.auto_id,
                                            prefix=self.prefix,
                                            initial={TOTAL_FORM_COUNT: self.total_form_count(),
                                                     INITIAL_FORM_COUNT: self.initial_form_count(),
                                                     MAX_NUM_FORM_COUNT: self.max_num},
                                            versions=[(form.instance.pk, get_revision_of_object(form.instance)) for form
                                                      in self.initial_forms])
        return form

    management_form = property(_management_form)


class ConcurrencyListEditableMixin(object):
    list_editable_policy = conf.POLICY

    def get_changelist_formset(self, request, **kwargs):
        kwargs['formset'] = ConcurrentBaseModelFormSet
        return super(ConcurrencyListEditableMixin, self).get_changelist_formset(request, **kwargs)

    def _add_conflict(self, request, obj):
        if hasattr(request, '_concurrency_list_editable_errors'):
            request._concurrency_list_editable_errors.append(obj.pk)
        else:
            request._concurrency_list_editable_errors = [obj.pk]

    def _get_conflicts(self, request):
        if hasattr(request, '_concurrency_list_editable_errors'):
            return request._concurrency_list_editable_errors
        else:
            return []

    def save_model(self, request, obj, form, change):
        try:
            if change:
                version = request.POST.get('_concurrency_version_{0.pk}'.format(obj), None)
                if version:
                    core._set_version(obj, version)
            super(ConcurrencyListEditableMixin, self).save_model(request, obj, form, change)
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
            return
        super(ConcurrencyListEditableMixin, self).log_change(request, object, message)

    def log_deletion(self, request, object, object_repr):
        if object.pk in self._get_conflicts(request):
            return
        super(ConcurrencyListEditableMixin, self).log_deletion(request, object, object_repr)

    def message_user(self, request, message, *args, **kwargs):
        # This is ugly but we do not want to touch the changelist_view() code.

        opts = self.model._meta
        conflicts = self._get_conflicts(request)
        if conflicts:
            names = force_text(opts.verbose_name), force_text(opts.verbose_name_plural)
            pattern = r"(?P<num>\d+) ({0}|{1})".format(*names)
            rex = re.compile(pattern)
            m = rex.match(message)
            concurrency_errros = len(conflicts)
            if m:
                updated_record = int(m.group('num')) - concurrency_errros

                ids = ",".join(map(str, conflicts))
                messages.error(request,
                               ungettext("Record with pk `{0}` has been modified and was not updated",
                                         "Records `{0}` have been modified and were not updated",
                                         concurrency_errros).format(ids))
                if updated_record == 1:
                    name = force_text(opts.verbose_name)
                else:
                    name = force_text(opts.verbose_name_plural)

                message = None
                if updated_record > 0:
                    message = ungettext("%(count)s %(name)s was changed successfully.",
                                        "%(count)s %(name)s were changed successfully.",
                                        updated_record) % {'count': updated_record,
                                                           'name': name}

        return super(ConcurrencyListEditableMixin, self).message_user(request, message, *args, **kwargs)


class ConcurrentModelAdmin(ConcurrencyActionMixin,
                           ConcurrencyListEditableMixin,
                           admin.ModelAdmin):
    form = ConcurrentForm
    formfield_overrides = {forms.VersionField: {'widget': VersionWidget}}
