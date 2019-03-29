from django.core.exceptions import ImproperlyConfigured

import pytest

from concurrency.config import AppSettings
from concurrency.utils import fqn


def test_config(settings):
    settings.APP_OVERRIDE = 'overridden'

    class MySettings(AppSettings):
        defaults = {'ENTRY1': 'abc',
                    'ENTRY2': 123,
                    'OVERRIDE': None,
                    'CALLBACK': fqn(fqn)}

    conf = MySettings("APP")
    assert str(conf.ENTRY1) == str(settings.APP_ENTRY1)

    assert str(conf.OVERRIDE) == str(settings.APP_OVERRIDE)

    conf = MySettings("MYAPP")
    assert conf.ENTRY2 == settings.MYAPP_ENTRY2

    settings.MYAPP_CALLBACK = fqn
    conf = MySettings("MYAPP")
    assert conf.CALLBACK == fqn

    with pytest.raises(ImproperlyConfigured):
        settings.OTHER_CALLBACK = 222
        conf = MySettings("OTHER")


def test_IGNORE_DEFAULT(settings):
    with pytest.raises(ImproperlyConfigured) as excinfo:
        settings.CONCURRENCY_IGNORE_DEFAULT = False
        AppSettings("")
    assert str(
        excinfo.value) == "IGNORE_DEFAULT has been removed in django-concurrency 1.5. Use VERSION_FIELD_REQUIRED instead"
