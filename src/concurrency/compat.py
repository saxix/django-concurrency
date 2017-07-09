# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import django

try:
    from django.template.base import TemplateDoesNotExist
except ImportError:
    from django.template.exceptions import TemplateDoesNotExist  # noqa - django 1.9

# try:
#     from django.db.transaction import atomic
# except ImportError:
#     from django.db.transaction import commit_on_success as atomic  # noqa
#

try:
    from django.urls.utils import get_callable
except ImportError:
    from django.core.urlresolvers import get_callable  # noqa

DJANGO_11 = django.VERSION[:2] == (1,11)
