from django.contrib import admin
import os

from django.conf import global_settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.test import TestCase
# from concurrency.tests.models import *
from concurrency.tests import TestModel0

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'concurrency')


class TestDjangoAdmin(TestCase):
    urls = 'concurrency.tests.urls'

    def setUp(self):
        super(TestDjangoAdmin, self).setUp()
        self.sett = self.settings(INSTALLED_APPS=INSTALLED_APPS,
            MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES,
            AUTHENTICATION_BACKENDS=global_settings.AUTHENTICATION_BACKENDS,
            PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',), # fastest hasher
            STATIC_URL='/static/',
            TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),),
#            TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',)

        )
        self.sett.enable()
        call_command('syncdb', verbosity=0)
        admin.site.register(TestModel0)
        self.user, __ = User.objects.get_or_create(username='sax', is_staff=True, is_superuser=True)
        self.user.set_password('123')
        self.user.save()
        self.client.login(username=self.user.username, password='123')
        self.target, __ = TestModel0.objects.get_or_create(username='aaa')

    def tearDown(self):
        super(TestDjangoAdmin, self).tearDown()
        self.sett.disable()
        admin.site.unregister(TestModel0)

    def test_standard_update(self):
        url = reverse('admin:concurrency_testmodel0_change', args=[self.target.pk])
        response = self.client.get(url)

        self.assertIn('original', response.context, response)
        target = response.context['original']
        old_version = target.version
        data = model_to_dict(target, exclude=['id'])

        data['username'] = 'new_username'
        data['_continue'] = 1
        data['date_field'] = '2010-09-01'

        response = self.client.post(url, data, follow=True)
        self.assertIn('original', response.context, response)
        self.assertFalse(response.context['adminform'].form.errors, response.context['adminform'].form.errors)
        target = response.context['original']
        new_version = target.version
        self.assertGreater(new_version, old_version)
