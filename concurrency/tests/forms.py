from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase
from demoapp.models import *

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'concurrency',
    'concurrency.tests.demoapp')


class ConcurrencyRequestTest(TestCase):
    urls = 'concurrency.tests.demoapp.urls'

    @classmethod
    def setUpClass(cls):
        super(ConcurrencyRequestTest, cls).setUpClass()

    def setUp(self):
        self.sett = self.settings(INSTALLED_APPS=set(settings.INSTALLED_APPS + INSTALLED_APPS))
        self.sett.enable()
        call_command('syncdb', verbosity=0)
        self.user = User.objects.create(username='sax')
        self.user.set_password('123')
        self.user.save()
        TestModel0.objects.create(username='aaa')
        super(ConcurrencyRequestTest, self).setUp()

    def tearDown(self):
        super(ConcurrencyRequestTest, self).tearDown()
        self.sett.disable()

    def test_concurrent_post(self):
        self.client.login(username='sax', password='123')
        url = reverse('admin:demoapp_testmodel0_change', args=[1])

