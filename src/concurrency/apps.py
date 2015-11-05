from __future__ import absolute_import, unicode_literals

try:
    from django.apps import AppConfig

    class ConcurrencyConfig(AppConfig):
        name = 'concurrency'
        verbose = 'Django Concurrency'

except ImportError:  # pragma: no cover
    pass
