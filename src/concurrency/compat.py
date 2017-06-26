# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# from django.core.urlresolvers import get_callable
# from django.db.transaction import atomic

try:
    from django.template.base import TemplateDoesNotExist
except ImportError:
    from django.template.exceptions import TemplateDoesNotExist  # noqa - django 1.9
