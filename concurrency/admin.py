## -*- coding: utf-8 -*-
#'''
#Created on 12/giu/2009
#
#@author: sax
#'''

from django.contrib import admin
from concurrency.forms import ConcurrentForm


class ConcurrentModelAdmin(admin.ModelAdmin):
    form = ConcurrentForm
