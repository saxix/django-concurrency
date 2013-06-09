from django.contrib.admin import ModelAdmin
from concurrency import forms, fields
from concurrency.admin import ConcurrencyActionMixin, ConcurrentModelAdmin
from concurrency.forms import ConcurrentForm
from .models import DemoModel
from functools import partial
from django.forms.models import modelform_factory, modelformset_factory
from concurrency import forms, fields
from concurrency.fields import VersionField


class DemoModelAdmin(ConcurrentModelAdmin):
    # list_display = [f.name for f in DemoModel._meta.fields]
    list_display = ('id', 'char', 'integer')
    list_display_links = ('id', )
    list_editable = ('char', 'integer')

