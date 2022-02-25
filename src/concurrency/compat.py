import django
from django.template.exceptions import TemplateDoesNotExist  # noqa
from django.urls.utils import get_callable  # noqa

if django.VERSION[:2] >= (4, 0):
    concurrency_param_name = 'form-_concurrency_version'
else:
    concurrency_param_name = '_concurrency_version'
