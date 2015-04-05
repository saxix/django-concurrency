import sys
import warnings
import pytest


def pytest_configure(config):
    warnings.simplefilter('default')

    try:
        from django.apps import AppConfig  # noqa
        import django

        django.setup()
    except ImportError:
        pass


windows = pytest.mark.skipif(sys.platform != 'win32', reason="requires windows")
