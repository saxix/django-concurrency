from django.apps import AppConfig


class ConcurrencyTestConfig(AppConfig):
    name = 'tests'
    label = 'tests'
    verbose_name = 'Concurrency Tests'
