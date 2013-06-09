## -*- coding: utf-8 -*-
from django.contrib import admin, messages
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.contrib.admin import helpers
from django.http import HttpResponse, HttpResponseRedirect
from concurrency.api import get_revision_of_object
from concurrency.exceptions import RecordModifiedError
from django.utils.encoding import force_text


class ConcurrencyActionMixin(object):
    check_concurrent_action = True

    def get_confirmation_template(self):
        return "concurrency/delete_selected_confirmation.html"

    def response_action(self, request, queryset):
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
        except ValueError:
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
            selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

            revision_field = self.model.RevisionMetaInfo.field
            if not selected:
                return None

            if self.check_concurrent_action:
                self.delete_selected_confirmation_template = self.get_confirmation_template()
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
                queryset = queryset.filter(*filters)
                if len(selected) != len(queryset):
                    messages.error(request, 'One or more record were updated. '
                                            '(Probably by other user) '
                                            'The execution was aborted.')
                    return HttpResponseRedirect(".")

            response = func(self, request, queryset)

            # Actions may return an HttpResponse, which will be used as the
            # response from the POST. If not, we'll be a good little HTTP
            # citizen and redirect back to the changelist page.
            if isinstance(response, HttpResponse):
                return response
            else:
                return HttpResponseRedirect(".")


class ConcurrentModelAdmin(ConcurrencyActionMixin, admin.ModelAdmin):
    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        """
        if self.list_editable:
            version = get_revision_of_object(obj)
            r = helpers.checkbox.render(helpers.ACTION_CHECKBOX_NAME,
                                        force_text("%s,%s" % (obj.pk, version)))
            return '{0}<input type="hidden" name="_concurrency_version_{2.pk}" value="{1}"'.format(r, version, obj)
        if self.check_concurrent_action:
            return helpers.checkbox.render(helpers.ACTION_CHECKBOX_NAME,
                                           force_text("%s,%s" % (obj.pk,
                                                                 get_revision_of_object(obj))))
        else:
            return super(ConcurrentModelAdmin, self).action_checkbox(obj)

    action_checkbox.short_description = mark_safe('<input type="checkbox" id="action-toggle" />')
    action_checkbox.allow_tags = True

    def save_model(self, request, obj, form, change):
        try:
            # if obj.pk is not None and not obj.version:
            obj.version = int(request.POST['_concurrency_version_{0.pk}'.format(obj)])
            super(ConcurrentModelAdmin, self).save_model(request, obj, form, change)
        except RecordModifiedError:
            messages.error(request, "Record with pk `{0.pk}` has been modified and was not updated".format(obj))
