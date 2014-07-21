
from django.apps import AppConfig


class ConcurrencyTestConfig(AppConfig):

    name = 'tests'
    label = 'tests'
    verbose_name = 'Concurrency Tests'


    def ready(self):
        from concurrency.api import apply_concurrency_check
        from django.contrib.auth.models import Permission
        from concurrency.fields import IntegerVersionField

        apply_concurrency_check(Permission, 'version', IntegerVersionField)

