import os
import sys
import warnings

# warnings.filterwarnings("ignore", category=DeprecationWarning)


def pytest_configure(config):
    from django.conf import settings
    sys.path.insert(0, os.path.dirname(__file__))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'demo.settings'
    warnings.simplefilter('default')

    try:
        from django.apps import AppConfig  # noqa
        import django
        django.setup()
    except ImportError:
        pass


def runtests(args=None):
    import pytest

    if not args:
        args = []

    if not any(a for a in args[1:] if not a.startswith('-')):
        args.append('concurrency')

    sys.exit(pytest.main(args))


if __name__ == '__main__':
    runtests(sys.argv)
