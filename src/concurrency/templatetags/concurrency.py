from __future__ import absolute_import, unicode_literals

from django.template import Library
from django.templatetags.l10n import unlocalize
from django.utils.safestring import mark_safe

from concurrency.api import get_revision_of_object
from concurrency.fields import VersionField

register = Library()


@register.filter
def identity(obj):
    """
    returns a string representing "<pk>,<version>" of the passed object
    """
    if hasattr(obj, '_concurrencymeta'):
        return mark_safe("{0},{1}".format(unlocalize(obj.pk),
                                          get_revision_of_object(obj)))
    else:
        return mark_safe(unlocalize(obj.pk))


@register.filter
def version(obj):
    """
    returns the value of the VersionField of the passed object
    """
    return get_revision_of_object(obj)


@register.filter
def is_version(field):
    """
    returns True if passed argument is a VersionField instance
    """
    return isinstance(field, VersionField)
