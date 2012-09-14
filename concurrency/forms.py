from django import forms
from django.forms import ModelForm, HiddenInput


class ConcurrentForm(ModelForm):
    version = forms.IntegerField(widget=HiddenInput())
