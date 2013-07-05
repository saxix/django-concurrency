from diff_match_patch import diff_match_patch
from concurrency.views import ConflictResponse
from django.template import loader
from django.utils.safestring import mark_safe
from django.template.context import RequestContext


def get_diff(current, stored):
    data = []
    dmp = diff_match_patch()
    fields = current._meta.fields
    for field in fields:
        v1 = getattr(current, field.name, "")
        v2 = getattr(stored, field.name, "")
        diff = dmp.diff_main(unicode(v1), unicode(v2))
        dmp.diff_cleanupSemantic(diff)
        html = dmp.diff_prettyHtml(diff)
        html = mark_safe(html)
        data.append((field, v1, v2, html))
    return data


def conflict(request, target=None, template_name='409.html'):
    template = loader.get_template(template_name)
    try:
        saved = target.__class__._default_manager.get(pk=target.pk)
        diff = get_diff(target, saved)
    except target.__class__.DoesNotExists:
        saved = None
        diff = None

    ctx = RequestContext(request, {'target': target,
                                   'diff': diff,
                                   'saved': saved,
                                   'request_path': request.path})
    return ConflictResponse(template.render(ctx))

