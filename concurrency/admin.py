## -*- coding: utf-8 -*-
#'''
#Created on 12/giu/2009
#
#@author: sax
#'''

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import helpers
from django.utils.encoding import force_unicode
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.util import unquote
from django.utils.functional import update_wrapper
from concurrency.fields import VersionField
from concurrency.forms import VersionWidget


class ConcurrentModelAdmin(admin.ModelAdmin):
    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        """
        return helpers.checkbox.render(helpers.ACTION_CHECKBOX_NAME, force_unicode("%s,%s" % (obj.pk, obj.version)))

    action_checkbox.short_description = mark_safe('<input type="checkbox" id="action-toggle" />')
    action_checkbox.allow_tags = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs.pop("request", None)
        if isinstance(db_field, VersionField):
            formfield = db_field.formfield(**kwargs)
            formfield.widget = VersionWidget()
            return formfield

        return super(admin.ModelAdmin, self).formfield_for_dbfield(db_field, request=request, **kwargs)

    def change_view(self, request, object_id, version_id=None, extra_context=None):
        if version_id:
            self.queryset(request).get(pk=unquote(object_id), _version=version_id)

        return super(ConcurrentModelAdmin, self).change_view(request, object_id, extra_context)

    def change_redir(self, request, object_id):
        obj = self.queryset(request).get(pk=unquote(object_id))
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        return HttpResponseRedirect(reverse('%sadmin_%s_%s_change' % info,
            args=[obj.pk, obj.version])
        )

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

            #
            # Orrible but work
            # absolutely need better code
            #
            if not selected:
                return None
            selection = {}
            for x in selected:
                pk, version = x.split(",")
                selection[int(pk)] = int(version)
            q = queryset.filter(pk__in=selection.keys())

            for i in q:
                if i.version != selection[i.pk]:
                    q = q.exclude(pk=i.pk)

            response = func(self, request, q)

            # Actions may return an HttpResponse, which will be used as the
            # response from the POST. If not, we'll be a good little HTTP
            # citizen and redirect back to the changelist page.
            if isinstance(response, HttpResponse):
                return response
            else:
                return HttpResponseRedirect(".")

    def get_urls(self):
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.changelist_view),
                name='%sadmin_%s_%s_changelist' % info),
            url(r'^add/$',
                wrap(self.add_view),
                name='%sadmin_%s_%s_add' % info),
            url(r'^(.+)/history/$',
                wrap(self.history_view),
                name='%sadmin_%s_%s_history' % info),
            url(r'^(.+)/delete/$',
                wrap(self.delete_view),
                name='%sadmin_%s_%s_delete' % info),
            url(r'^(.+),(.+)/$',
                wrap(self.change_view),
                name='%sadmin_%s_%s_change' % info),
            url(r'^(.+)/$',
                self.change_redir,
                name='%sadmin_%s_%s_change' % info),
        )
        return urlpatterns
