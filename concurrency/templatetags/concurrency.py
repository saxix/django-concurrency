from __future__ import absolute_import
from django.template import Library
from django.templatetags.l10n import unlocalize
from django.utils.safestring import mark_safe
from concurrency.api import get_revision_of_object

register = Library()


@register.filter
def identity(obj):
    return mark_safe("{0},{1}".format(unlocalize(obj.pk), get_revision_of_object(obj)))


@register.filter
def version(obj):
    return get_revision_of_object(obj)
