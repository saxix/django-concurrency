from __future__ import absolute_import, unicode_literals

from importlib import import_module

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ImproperlyConfigured, ValidationError
from django.core.signing import BadSignature, Signer
from django.forms import HiddenInput, ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from concurrency.config import conf
from concurrency.core import _select_lock
from concurrency.exceptions import RecordModifiedError, VersionError


class ConcurrentForm(ModelForm):
    """ Simple wrapper to ModelForm that try to mitigate some concurrency error.
        Note that is always possible have a RecordModifiedError in model.save().
        Statistically form.clean() should catch most of the concurrent editing, but
        is good to catch RecordModifiedError in the view too.
    """

    def clean(self):
        try:
            if self.instance.pk:
                _select_lock(self.instance, self.cleaned_data[self.instance._concurrencymeta.field.name])

        except RecordModifiedError:
                self._update_errors(ValidationError({NON_FIELD_ERRORS: self.error_class([_('Record Modified')])}))

        return super(ConcurrentForm, self).clean()


class VersionWidget(HiddenInput):
    """
    Widget that show the revision number using <div>

    Usually VersionField use `HiddenInput` as Widget to minimize the impact on the
    forms, in the Admin this produce a side effect to have the label *Version* without
    any value, you should use this widget to display the current revision number
    """

    def _format_value(self, value):
        if value:
            value = str(value)
        return value

    def render(self, name, value, attrs=None):
        ret = super(VersionWidget, self).render(name, value, attrs)
        label = ''
        if isinstance(value, SignedValue):
            label = str(value).split(':')[0]
        elif value is not None:
            label = str(value)

        return mark_safe("%s<div>%s</div>" % (ret, label))


class VersionFieldSigner(Signer):
    def sign(self, value):
        if not value:
            return None
        return super(VersionFieldSigner, self).sign(value)


def get_signer():
    path = conf.FIELD_SIGNER
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error loading concurrency signer %s: "%s"' % (module, e))
    try:
        signer_class = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a valid signer named "%s"' % (module, attr))
    return signer_class()


class SignedValue(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        if self.value:
            return str(self.value)
        else:
            return ''


class VersionField(forms.IntegerField):
    widget = HiddenInput  # Default widget to use when rendering this type of Field.
    hidden_widget = HiddenInput  # Default widget to use when rendering this as "hidden".

    def __init__(self, *args, **kwargs):
        self._signer = kwargs.pop('signer', get_signer())
        kwargs.pop('min_value', None)
        kwargs.pop('max_value', None)
        kwargs['required'] = True
        kwargs['initial'] = None
        kwargs.setdefault('widget', HiddenInput)
        super(VersionField, self).__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        return SignedValue(data)

    def prepare_value(self, value):
        if isinstance(value, SignedValue):
            return value
        elif value is None:
            return ''
        return SignedValue(self._signer.sign(value))

    def to_python(self, value):
        try:
            if value not in (None, '', 'None'):
                return int(self._signer.unsign(value))
            return 0
        except (BadSignature, ValueError):
            raise VersionError(value)

    def widget_attrs(self, widget):
        return {}
