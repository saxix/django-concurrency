from __future__ import absolute_import
from django.template import Library
from concurrency.api import get_revision_of_object

register = Library()


@register.filter
def version(obj):
    return get_revision_of_object(obj)
