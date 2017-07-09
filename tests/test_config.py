import pytest
from django.core.exceptions import ImproperlyConfigured

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
