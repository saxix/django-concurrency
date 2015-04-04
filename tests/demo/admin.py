from django.contrib.admin.sites import NotRegistered
from django.contrib import admin
from concurrency.admin import ConcurrentModelAdmin
from .models import *  # noqa
from .models import NoActionsConcurrentModel, ListEditableConcurrentModel


class ListEditableModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'username')
    list_editable = ('username', )
    ordering = ('id', )


class NoActionsModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'username')
    list_editable = ('username', )
    ordering = ('id', )
    actions = None


class ActionsModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'username')
    actions = ['dummy_action']
    ordering = ('id', )

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


admin_register_models()
