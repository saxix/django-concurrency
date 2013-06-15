from __future__ import absolute_import, unicode_literals
from six import string_types
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed
from concurrency.utils import import_by_path


# List Editable Policy
# 0 do not save updated records, save others, show message to the user
# 1 abort whole transaction

CONCURRENCY_LIST_EDITABLE_POLICY_SILENT = 0
CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL = 1


class AppSettings(object):
    """
    Class to manage application related settings
    How to use:

    >>> from django.conf import settings
    >>> settings.APP_OVERRIDE = 'overridden'
    >>> settings.MYAPP_CALLBACK = 100
    >>> class MySettings(AppSettings):
    ...     defaults = {'ENTRY1': 'abc', 'ENTRY2': 123, 'OVERRIDE': None, 'CALLBACK':10}
    ...     def set_CALLBACK(self, value):
    ...         setattr(self, 'CALLBACK', value*2)

    >>> conf = MySettings("APP")
    >>> conf.ENTRY1, settings.APP_ENTRY1
    ('abc', 'abc')
    >>> conf.OVERRIDE, settings.APP_OVERRIDE
    ('overridden', 'overridden')

    >>> conf = MySettings("MYAPP")
    >>> conf.ENTRY2, settings.MYAPP_ENTRY2
    (123, 123)
    >>> conf = MySettings("MYAPP")
    >>> conf.CALLBACK
    200

    """
    defaults = {
        'SANITY_CHECK': True,
        'FIELD_SIGNER': 'concurrency.forms.VersionFieldSigner',
        'LIST_EDITABLE_POLICY': CONCURRENCY_LIST_EDITABLE_POLICY_SILENT,
        'HANDLER409': 'concurrency.views.conflict'}

    def __init__(self, prefix):
        """
        Loads our settings from django.conf.settings, applying defaults for any
        that are omitted.
        """
        self.prefix = prefix
        from django.conf import settings

        for name, default in self.defaults.items():
            prefix_name = (self.prefix + '_' + name).upper()
            value = getattr(settings, prefix_name, default)
            self._set_attr(prefix_name, value)
            setattr(settings, prefix_name, value)
            setting_changed.send(self, setting=prefix_name, value=value)

        setting_changed.connect(self._handler)

    def _set_attr(self, prefix_name, value):
        name = prefix_name[len(self.prefix) + 1:]
        setattr(self, name, value)

    def _handler(self, sender, setting, value, **kwargs):
        """
            handler for ``setting_changed`` signal.

        @see :ref:`django:setting-changed`_
        """
        if setting.startswith(self.prefix):
            self._set_attr(setting, value)

    def _import_by_path(self, attrname, value):
        processed = None
        if isinstance(value, (list, tuple)):
            processed = []
            for entry in value:
                processed.append(import_by_path(entry))
        elif isinstance(value, string_types):
            processed = import_by_path(value)

        if processed is not None:
            setattr(self, attrname, processed)
        else:
            raise ImproperlyConfigured('Cannot import by path `%s`' % value)


conf = AppSettings('CONCURRENCY')
