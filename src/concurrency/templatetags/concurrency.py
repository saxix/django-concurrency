from django.template import Library
from django.templatetags.l10n import unlocalize
from django.utils.html import format_html

from concurrency.api import get_revision_of_object
from concurrency.fields import VersionField

register = Library()


@register.filter
def identity(obj):
    """Return a string representing "<pk>,<version>" of the passed object."""
    if hasattr(obj, "_concurrencymeta"):
        return format_html("{},{}", unlocalize(obj.pk), get_revision_of_object(obj))
    return format_html("{}", unlocalize(obj.pk))


@register.filter
def version(obj):
    """Return the value of the VersionField of the passed object."""
    return get_revision_of_object(obj)


@register.filter
def is_version(field):
    """Return True if passed argument is a VersionField instance."""
    return isinstance(field, VersionField)
