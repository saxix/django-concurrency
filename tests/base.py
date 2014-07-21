import django
import pytest
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django_webtest import WebTestMixin
from tests.admin import admin_register_models

SENTINEL = '**concurrent_update**'

from concurrency.api import apply_concurrency_check
from django.contrib.auth.models import Permission
from concurrency.fields import IntegerVersionField

apply_concurrency_check(Permission, 'version', IntegerVersionField)

DJANGO_TRUNK = django.VERSION[:2] >= (1, 8)

win32only = pytest.mark.skipif("sys.platform != 'win32'")

skipIfDjangoVersion = lambda v: pytest.mark.skipif(django.VERSION[:2] >= v,
                                                   reason="Skip if django>={}".format(v))


class AdminTestCase(WebTestMixin, TransactionTestCase):
    urls = 'tests.urls'

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.user, __ = User.objects.get_or_create(is_superuser=True,
                                                   is_staff=True,
                                                   is_active=True,
                                                   email='sax@example.com',
                                                   username='sax')

        admin_register_models()
