import os
import platform
import sys

import django

import pytest

py_impl = getattr(platform, 'python_implementation', lambda: None)
PYPY = py_impl() == 'PyPy'
PURE_PYTHON = os.environ.get('PURE_PYTHON', False)

windows = pytest.mark.skipif(sys.platform != 'win32', reason="requires windows")

win32only = pytest.mark.skipif("sys.platform != 'win32'")

skippypy = pytest.mark.skipif(PYPY, reason='skip on pypy')

# skipIfDjangoVersion = lambda v: pytest.mark.skipif("django.VERSION[:2]>={}".format(v),
#                                                    reason="Skip if django>={}".format(v))


def pytest_configure():
    from django.contrib.auth.models import Group
    from django.conf import settings

    settings.SILENCED_SYSTEM_CHECKS = ['concurrency.W001']
    if django.VERSION[:2] == (1.6):
        from concurrency.api import apply_concurrency_check
        from concurrency.fields import IntegerVersionField

        apply_concurrency_check(Group, 'version', IntegerVersionField)


@pytest.fixture(scope='session')
def client(request):
    import django_webtest

    wtm = django_webtest.WebTestMixin()
    wtm.csrf_checks = False
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    app = django_webtest.DjangoTestApp()
    return app
