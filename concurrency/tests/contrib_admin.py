import re
import os
import django.core.management
from django.contrib import admin
from django.conf import global_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.test import TestCase
from concurrency import forms
from concurrency.forms import ConcurrentForm, VersionWidget, VersionFieldSigner
from concurrency.tests import TestModel0, TestModel1
from django.utils.translation import ugettext as _

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.admindocs',
    'django.contrib.admin',
    'concurrency')


class TestModel1Admin(admin.ModelAdmin):
    formfield_overrides = {
        forms.VersionField: {'widget': VersionWidget()},
    }
    form = modelform_factory(TestModel1, ConcurrentForm,
                             widgets={'version': VersionWidget()})


class DjangoAdminTestCase(TestCase):
    urls = 'concurrency.tests.urls'
    MIDDLEWARE_CLASSES = global_settings.MIDDLEWARE_CLASSES
    AUTHENTICATION_BACKENDS = global_settings.AUTHENTICATION_BACKENDS

    def setUp(self):
        super(DjangoAdminTestCase, self).setUp()
        self.sett = self.settings(INSTALLED_APPS=INSTALLED_APPS,
                                  MIDDLEWARE_CLASSES=self.MIDDLEWARE_CLASSES,
                                  AUTHENTICATION_BACKENDS=self.AUTHENTICATION_BACKENDS,
                                  PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',), # fastest hasher
                                  STATIC_URL='/static/',
                                  SOUTH_TESTS_MIGRATE=False,
                                  TEMPLATE_DIRS=(os.path.join(os.path.dirname(__file__), 'templates'),),
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
        super(DjangoAdminTestCase, self).tearDown()
        self.sett.disable()
        admin.site.unregister(TestModel0)
        admin.site.unregister(TestModel1)


class TestDjangoAdmin(DjangoAdminTestCase):

    def test_creation(self):
        url = reverse('admin:concurrency_testmodel0_add')
        data = {'username': 'new_username',
                'last_name': None,
                'version': VersionFieldSigner().sign(None),
                'char_field': None,
                '_continue': 1,
                'date_field': '2010-09-01'}

        self.client.post(url, data, follow=True)
        self.assertTrue(TestModel0.objects.filter(username='new_username').exists())
        self.assertGreater(TestModel0.objects.get(username='new_username').version, 0)

    def test_creation_with_customform(self):
        url = reverse('admin:concurrency_testmodel1_add')
        data = {'username': 'new_username',
                'last_name': None,
                'version': VersionFieldSigner().sign(0),
                'char_field': None,
                '_continue': 1,
                'date_field': '2010-09-01'}

        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TestModel1.objects.filter(username='new_username').exists())
        self.assertGreater(TestModel1.objects.get(username='new_username').version, 0)

        # test no other errors are raised
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test model0 with this Username already exists.")

    def test_standard_update(self):
        url = reverse('admin:concurrency_testmodel0_change', args=[self.target.pk])
        response = self.client.get(url)
        self.assertIn('original', response.context, response)
        target = response.context['original']
        old_version = target.version
        # data = model_to_dict(target, exclude=['id'])
        data = {'username': 'new_username',
                'last_name': None,
                'version': VersionFieldSigner().sign(target.version),
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
        form = response.context['adminform'].form
        version = int(str(form['version'].value()).split(":")[0])

        data = {'username': 'new_username',
                'last_name': None,
                'version': VersionFieldSigner().sign(version),
                'char_field': None,
                '_continue': 1,
                'date_field': '2010-09-01'}

        self.target1.save() # create conflict here

        response = self.client.post(url, data, follow=True)
        self.assertIn('original', response.context, response)
        self.assertTrue(response.context['adminform'].form.errors,
                        response.context['adminform'].form.errors)
        self.assertIn(_('Record Modified'),
                      str(response.context['adminform'].form.errors),
                      response.context['adminform'].form.errors)

    def test_sanity_signer(self):
        url = reverse('admin:concurrency_testmodel1_change', args=[self.target1.pk])
        response = self.client.get(url)
        self.assertIn('original', response.context, response)
        form = response.context['adminform'].form
        version1 = int(str(form['version'].value()).split(":")[0])


        data = {'username': 'new_username',
                'last_name': None,
                'version': VersionFieldSigner().sign(version1),
                'char_field': None,
                '_continue': 1,
                'date_field': 'esss2010-09-01'}

        response = self.client.post(url, data, follow=True)
        self.assertIn('original', response.context, response)
        self.assertTrue(response.context['adminform'].form.errors,
                        response.context['adminform'].form.errors)
        form = response.context['adminform'].form
        version2 = int(str(form['version'].value()).split(":")[0])
        self.assertEqual(version1, version2)
