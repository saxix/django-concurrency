import os
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import NotRegistered
import django.core.management
from django.contrib import admin
from django.conf import global_settings
from django.contrib.auth.models import User
from django.forms.models import modelform_factory
from django.test import TestCase
from django_webtest import WebTest
from concurrency import forms
from concurrency.admin import ConcurrentModelAdmin
from concurrency.forms import ConcurrentForm, VersionWidget
from concurrency.tests.models import (TestModel0, TestModel1, ConcurrentModel, ListEditableConcurrentModel,
                                      NoActionsConcurrentModel)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'concurrency')

SENTINEL = '**concurrent_update**'


def admin_register(model, modeladmin=ConcurrentModelAdmin):
    try:
        admin.site.unregister(model)
    except NotRegistered:  # pragma: no cover
        pass
    admin.site.register(model, modeladmin)


def admin_unregister(*models):
    for m in models:
        try:
            admin.site.unregister(m)
        except NotRegistered:  # pragma: no cover
            pass


class TestModel1Admin(admin.ModelAdmin):
    formfield_overrides = {
        forms.VersionField: {'widget': VersionWidget()},
    }
    form = modelform_factory(TestModel1, ConcurrentForm,
                             widgets={'version': VersionWidget()})


class ListEditableModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'dummy_char')
    list_editable = ('dummy_char', )
    ordering = ('id', )


class NoActionsModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'dummy_char')
    list_editable = ('dummy_char', )
    ordering = ('id', )
    actions = None


class ActionsModelAdmin(ConcurrentModelAdmin):
    list_display = ('__unicode__', 'version', 'dummy_char')
    actions = ['dummy_action']
    ordering = ('id', )

    def dummy_action(self, request, queryset):
        for el in queryset:
            el.dummy_char = '**action_update**'
            el.save()


class AdminTestCase(WebTest):
    urls = 'concurrency.tests.urls'

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.user, __ = User.objects.get_or_create(is_superuser=True,
                                                   is_staff=True,
                                                   is_active=True,
                                                   email='sax@example.com',
                                                   username='sax')
        for i in range(1, 10):
            ConcurrentModel.objects.get_or_create(id=i, version=0, dummy_char=str(i))

        admin_register(ConcurrentModel, ActionsModelAdmin)
        admin_register(ListEditableConcurrentModel, ListEditableModelAdmin)
        admin_register(NoActionsConcurrentModel, NoActionsModelAdmin)
        admin_register(TestModel1, TestModel1Admin)
        admin_register(TestModel0, ModelAdmin)


class DjangoAdminTestCase(TestCase):
    urls = 'concurrency.tests.urls'
    MIDDLEWARE_CLASSES = global_settings.MIDDLEWARE_CLASSES
    AUTHENTICATION_BACKENDS = global_settings.AUTHENTICATION_BACKENDS

    def setUp(self):
        super(DjangoAdminTestCase, self).setUp()
        self.sett = self.settings(
                                #INSTALLED_APPS=INSTALLED_APPS,
                                  MIDDLEWARE_CLASSES=self.MIDDLEWARE_CLASSES,
                                  AUTHENTICATION_BACKENDS=self.AUTHENTICATION_BACKENDS,
                                  PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',),  # fastest hasher
                                  STATIC_URL='/static/',
                                  SOUTH_TESTS_MIGRATE=False,
                                  TEMPLATE_DIRS=(os.path.join(os.path.dirname(__file__), 'templates'),))
        self.sett.enable()
        django.core.management._commands = None  # reset commands cache
        django.core.management.call_command('syncdb', verbosity=0)

        admin_register(TestModel0)
        admin_register(TestModel1, TestModel1Admin)

        self.user, __ = User.objects.get_or_create(username='sax', is_staff=True,
                                                   is_superuser=True)
        self.user.set_password('123')
        self.user.save()
        self.client.login(username=self.user.username, password='123')
        self.target, __ = TestModel0.objects.get_or_create(username='aaa')
        self.target1, __ = TestModel1.objects.get_or_create(username='bbb')

    def tearDown(self):
        super(DjangoAdminTestCase, self).tearDown()
        self.sett.disable()
        admin_unregister(TestModel0, TestModel1)
