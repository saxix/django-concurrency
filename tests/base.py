import os
from django.test import TransactionTestCase, TestCase
import django.core.management
from django.conf import global_settings
from django.contrib.auth.models import User
from django_webtest import WebTestMixin

SENTINEL = '**concurrent_update**'


class AdminTestCase(WebTestMixin, TestCase):
    urls = 'tests.urls'

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.user, __ = User.objects.get_or_create(is_superuser=True,
                                                   is_staff=True,
                                                   is_active=True,
                                                   email='sax@example.com',
                                                   username='sax')

    def tearDown(self):
        super(AdminTestCase, self).tearDown()


class DjangoAdminTestCase(TransactionTestCase):
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

        # admin_register(TestModel0)
        # admin_register(TestModel1, TestModel1Admin)

        self.user, __ = User.objects.get_or_create(username='sax',
                                                   is_active=True,
                                                   is_staff=True,
                                                   is_superuser=True)
        self.user.set_password('123')
        self.user.save()
        self.client.login(username=self.user.username, password='123')
        # self.target, __ = TestModel0.objects.get_or_create(username='aaa')
        # self.target1, __ = TestModel1.objects.get_or_create(username='bbb')

    def tearDown(self):
        super(DjangoAdminTestCase, self).tearDown()
        self.sett.disable()
        # admin_unregister(TestModel0, TestModel1)
