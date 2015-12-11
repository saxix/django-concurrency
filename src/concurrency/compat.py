# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

try:
    from django.template.base import TemplateDoesNotExist
except ImportError:
    from django.template.exceptions import TemplateDoesNotExist  # noqa - django 1.9

try:
    from django.db.transaction import atomic
except ImportError:
    from django.db.transaction import commit_on_success as atomic  # noqa
