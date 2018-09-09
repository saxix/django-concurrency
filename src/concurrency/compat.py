# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import django

# if django.VERSION <(1,9):
#     from django.template.base import TemplateDoesNotExist
# else:
from django.template.exceptions import TemplateDoesNotExist  # noqa - django 1.9

# if django.VERSION <(1,9):
#     from django.core.urlresolvers import get_callable  # noqa
# else:
from django.urls.utils import get_callable
