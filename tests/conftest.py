import sys
import warnings


def pytest_configure(config):
    warnings.simplefilter('default')

    try:
        from django.apps import AppConfig  # noqa
        import django

        django.setup()
    except ImportError:
        pass
