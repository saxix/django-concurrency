import sys
import warnings
import django
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
skip14 = pytest.mark.skipif(django.VERSION[0:2] == [1, 4], reason="skip django 1.4")
skip15 = pytest.mark.skipif(django.VERSION[0:2] == [1, 5], reason="skip django 1.4")
