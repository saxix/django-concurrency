.. include:: globals.txt

.. _middleware:

ConcurrencyMiddleware
=====================

You can globally intercept :class:`RecordModifiedError <concurrency.exceptions.RecordModifiedError>`
adding :class:`ConcurrencyMiddleware <concurrency.middleware.ConcurrencyMiddleware>` to your :setting:`MIDDLEWARE_CLASSES`.
Each time a :class:`RecordModifiedError <concurrency.exceptions.RecordModifiedError>` is raised it goes up to the ConcurrencyMiddleware and the handler defined in
:setting:`CONCURRENCY_HANDLER409` is invoked.

**Example**

``settings.py``

.. code-block:: python

        MIDDLEWARE_CLASSES=('django.middleware.common.CommonMiddleware',
                            'concurrency.middleware.ConcurrencyMiddleware',
                            'django.contrib.sessions.middleware.SessionMiddleware',
                            'django.middleware.csrf.CsrfViewMiddleware',
                            'django.contrib.auth.middleware.AuthenticationMiddleware',
                            'django.contrib.messages.middleware.MessageMiddleware')

        CONCURRENCY_HANDLER409 = 'demoproject.demoapp.views.conflict'
        CONCURRENCY_POLICY = 2  # CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL

:file:`views.py`

.. code-block:: python

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



:file:`409.html`

.. code-block:: html

    {% load concurrency %}
    <table>
        <tr>
            <th>
                Field
            </th>
            <th>
                Current
            </th>
            <th>
                Stored
            </th>
            <th>
                Diff
            </th>

        </tr>
        <tr>
            {% for field, current, stored, entry in diff %}
                {% if not field.primary_key and not field|is_version %}
                    <tr>
                        <td>
                            {{ field.verbose_name }}
                        </td>
                        <td>
                            {{ current }}
                        </td>
                        <td>
                            {{ stored }}
                        </td>
                        <td>
                            {{ entry }}
                        </td>
                    </tr>
                {% endif %}
            {% endfor %}
        </tr>
    </table>

If you want to use ConcurrentMiddleware in the admin and you are using
:class:`concurrency.admin.ConcurrentModelAdmin` remember to set your ModelAdmin to NOT
use :class:`concurrency.forms.ConcurrentForm`

.. code-block:: python

    from django import forms

    class MyModelAdmin(ConcurrentModelAdmin):
        form = forms.ModelForm  # overrides default ConcurrentForm

