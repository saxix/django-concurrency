# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirectBase, HttpResponse


class HttpResponseConflict(HttpResponse):
    status_code = 409

    def __init__(self):
        super(HttpResponse, self).__init__()
