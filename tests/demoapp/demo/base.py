from demo.admin import admin_register_models
from django.contrib.auth.models import Group, User
from django.test import TransactionTestCase
from django.utils import timezone
from django_webtest import WebTestMixin

from concurrency.api import apply_concurrency_check
from concurrency.fields import IntegerVersionField

SENTINEL = '**concurrent_update**'


apply_concurrency_check(Group, 'version', IntegerVersionField)


class AdminTestCase(WebTestMixin, TransactionTestCase):
    urls = 'demo.urls'

    def setUp(self):
        super().setUp()

        self.user, __ = User.objects.get_or_create(is_superuser=True,
                                                   is_staff=True,
                                                   is_active=True,
                                                   last_login=timezone.now(),
                                                   email='sax@example.com',
                                                   username='sax')
        admin_register_models()
