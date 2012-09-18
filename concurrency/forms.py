from django import forms
from django.core import exceptions
from django.forms import ModelForm, HiddenInput
from django.utils.safestring import mark_safe


class ConcurrentForm(ModelForm):
    version = forms.IntegerField(widget=HiddenInput())

    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        original = super(ConcurrentForm, self)._html_output(normal_row, error_row, row_ender, help_text_html,
            errors_on_separate_row)
        return original


class VersionWidget(HiddenInput):
    """
    Widget that show the revision number using <div>

    Usually VersionField is use `HiddenInput` as Widget to minimize the impact on the
    forms, in the Admin this produce a side effect to have the label *Version* without
    any value, to display the current revision number is possible to use this filed
    """

    def render(self, name, value, attrs=None):
        ret = super(VersionWidget, self).render(name, value, attrs)
        return mark_safe("%s<div>%s</div>" % (ret, value))


class VersionField(forms.IntegerField):
    widget = HiddenInput # Default widget to use when rendering this type of Field.
    hidden_widget = HiddenInput # Default widget to use when rendering this as "hidden".

    def __init__(self, *args, **kwargs):
        kwargs.pop('max_value', None)
        kwargs.pop('max_value', None)
        kwargs['required'] = True
        kwargs['initial'] = None
        super(VersionField, self).__init__(None, None, *args, **kwargs)

    def clean(self, value):
        return super(VersionField, self).clean(value)

    def to_python(self, value):
        if value is None:
            return 0
        try:
            value = int(str(value))
        except (ValueError, TypeError):
            value=0
        return value

    def widget_attrs(self, widget):
        """
        Given a Widget instance (*not* a Widget class), returns a dictionary of
        any HTML attributes that should be added to the Widget, based on this
        Field.
        """
        return {}
