import os
import sys
from django.conf import settings



def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, here)

    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

    from concurrency.api import apply_concurrency_check
    from django.contrib.auth.models import Permission
    from concurrency.fields import IntegerVersionField
    apply_concurrency_check(Permission, 'version', IntegerVersionField)

def runtests(args=None):
    import pytest

    if not args:
        args = []

    if not any(a for a in args[1:] if not a.startswith('-')):
        args.append('concurrency')

    sys.exit(pytest.main(args))


if __name__ == '__main__':
    runtests(sys.argv)
