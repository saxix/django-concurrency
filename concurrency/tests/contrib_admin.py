from django.contrib import admin
import os

from django.conf import global_settings
from django.contrib.auth.models import User
import django.core.management
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.forms.models import modelform_factory
from django.test import TestCase
# from concurrency.tests.models import *
from concurrency import forms
from concurrency.fields import VersionField, AutoIncVersionField, IntegerVersionField
from concurrency.forms import ConcurrentForm, VersionWidget
from concurrency.tests import TestModel0, TestModel1

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django.contrib.admin',
    'concurrency')


class TestModel1Admin(admin.ModelAdmin):
    formfield_overrides = {
        # VersionField: {'widget': VersionWidget},
        forms.VersionField: {'widget': VersionWidget()},
        # IntegerVersionField: {'widget': VersionWidget},
        # AutoIncVersionField: {'widget': VersionWidget},
    }
    form = modelform_factory(TestModel1, ConcurrentForm,
                             widgets={'version': VersionWidget()})


class TestDjangoAdmin(TestCase):
    urls = 'concurrency.tests.urls'

    def setUp(self):
        super(TestDjangoAdmin, self).setUp()
        self.sett = self.settings(INSTALLED_APPS=INSTALLED_APPS,
                                  MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES,
                                  AUTHENTICATION_BACKENDS=global_settings.AUTHENTICATION_BACKENDS,
                                  PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',), # fastest hasher
                                  STATIC_URL='/static/',
                                  SOUTH_TESTS_MIGRATE=False,
                                  TEMPLATE_DIRS=(os.path.join(os.path.dirname(__file__), 'templates'),),
                                  #            TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',)

        )
        self.sett.enable()
        django.core.management._commands = None # reset commands cache
        django.core.management.call_command('syncdb', verbosity=0)
        admin.site.register(TestModel0)
        admin.site.register(TestModel1, TestModel1Admin)
        self.user, __ = User.objects.get_or_create(username='sax', is_staff=True, is_superuser=True)
        self.user.set_password('123')
        self.user.save()
        self.client.login(username=self.user.username, password='123')
        self.target, __ = TestModel0.objects.get_or_create(username='aaa')
        self.target1, __ = TestModel1.objects.get_or_create(username='bbb')

    def tearDown(self):
        super(TestDjangoAdmin, self).tearDown()
        self.sett.disable()
        admin.site.unregister(TestModel0)
        admin.site.unregister(TestModel1)

    def test_standard_update(self):
        url = reverse('admin:concurrency_testmodel0_change', args=[self.target.pk])
        response = self.client.get(url)
        self.assertIn('original', response.context, response)
        target = response.context['original']
        old_version = target.version
        # data = model_to_dict(target, exclude=['id'])
        data = {'username': u'new_username',
                'last_name': None,
                'version': Signer().sign(target.version),
                'char_field': None,
                '_continue': 1,
                'date_field': '2010-09-01'}

        response = self.client.post(url, data, follow=True)
        self.assertIn('original', response.context, response)
        self.assertFalse(response.context['adminform'].form.errors, response.context['adminform'].form.errors)
        target = response.context['original']
        new_version = target.version
        self.assertGreater(new_version, old_version)

    def test_conflict(self):
        url = reverse('admin:concurrency_testmodel1_change', args=[self.target1.pk])
        response = self.client.get(url)
        self.assertIn('original', response.context, response)
        target = response.context['original']

        data = {'username': u'new_username',
                'last_name': None,
                'version': response.context['adminform'].form['version'].value(),
                'char_field': None,
                '_continue': 1,
                'date_field': '2010-09-01'}

        self.target1.save() # conflict here

        response = self.client.post(url, data, follow=True)
        self.assertIn('original', response.context, response)
        self.assertTrue(response.context['adminform'].form.errors, response.context['adminform'].form.errors)
        self.assertIn('Record Modified', str(response.context['adminform'].form.errors),
                      response.context['adminform'].form.errors)
        target = response.context['original']
