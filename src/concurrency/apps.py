from __future__ import absolute_import, unicode_literals

try:
    from django.apps import AppConfig
except ImportError:  # pragma no cover
    AppConfig = object


class ConcurrencyConfig(AppConfig):
    name = 'concurrency'
    verbose = 'Django Concurrency'
