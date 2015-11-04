# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import HttpResponse
from django.template import loader
from django.template.base import Template
from django.template.context import RequestContext
from django.utils.translation import ugettext as _

from concurrency.compat import TemplateDoesNotExist
from concurrency.exceptions import RecordModifiedError


class ConflictResponse(HttpResponse):
    status_code = 409


def callback(target, *args, **kwargs):
    raise RecordModifiedError(_('Record has been modified'), target=target)


def conflict(request, target=None, template_name='409.html'):
    """409 error handler.

    :param request: Request

    :param template_name: `409.html`

    :param target: The model to save

    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        template = Template(
            '<h1>Conflict</h1>'
            '<p>The request was unsuccessful due to a conflict. '
            'The object changed during the transaction.</p>')
    try:
        saved = target.__class__._default_manager.get(pk=target.pk)
    except target.__class__.DoesNotExist:
        saved = None
    ctx = RequestContext(request, {'target': target,
                                   'saved': saved,
                                   'request_path': request.path})
    return ConflictResponse(template.render(ctx))
