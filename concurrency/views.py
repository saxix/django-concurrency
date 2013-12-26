# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.template import loader
from django.template.base import TemplateDoesNotExist, Template
from django.template.context import RequestContext
from concurrency.exceptions import RecordModifiedError


class ConflictResponse(HttpResponse):
    status_code = 409


handler409 = 'concurrency.views.conflict'


def callback(target, *args, **kwargs):
    raise RecordModifiedError(_('Record has been modified'), target=target)


def conflict(request, target=None, template_name='409.html'):
    """409 error handler.

    Templates: `409.html`
    Context:
    `target` : The model to save
    `saved`  : The object stored in the db that produce the conflict or None if not found (ie. deleted)
    `request_path` : The path of the requested URL (e.g., '/app/pages/bad_page/')

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
