from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.sites import NotRegistered

from demo.models import *  # noqa
from demo.models import (
    ListEditableConcurrentModel, NoActionsConcurrentModel, ReversionConcurrentModel
)

from concurrency.admin import ConcurrentModelAdmin
from concurrency.api import disable_concurrency

try:
    from reversion import VersionAdmin
except ImportError:
    class VersionAdmin(object):
        pass


class ListEditableModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'username')
    list_editable = ('username',)
    ordering = ('id',)


class NoActionsModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'username')
    list_editable = ('username',)
    ordering = ('id',)
    actions = None


class ReversionConcurrentModelAdmin(VersionAdmin, ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'username')
    list_editable = ('username',)
    ordering = ('id',)
    actions = None

    @disable_concurrency()
    def recover_view(self, request, version_id, extra_context=None):
        return super(ReversionConcurrentModelAdmin, self).recover_view(request,
                                                                       version_id,
                                                                       extra_context)


class ActionsModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'username')
    actions = ['dummy_action']
    ordering = ('id',)

    def dummy_action(self, request, queryset):
        for el in queryset:
            el.username = '**action_update**'
            el.save()


def admin_register(model, modeladmin=ConcurrentModelAdmin):
    try:
        admin.site.unregister(model)
    except NotRegistered:  # pragma: no cover
        pass
    admin.site.register(model, modeladmin)


def admin_register_models():
    admin_register(SimpleConcurrentModel, ActionsModelAdmin)
    admin_register(ProxyModel, ListEditableModelAdmin)
    admin_register(InheritedModel, ActionsModelAdmin)
    admin_register(NoActionsConcurrentModel, NoActionsModelAdmin)
    admin_register(ListEditableConcurrentModel, ListEditableModelAdmin)
    admin_register(ReversionConcurrentModel, ReversionConcurrentModelAdmin)


admin_register_models()
