# -*- coding: utf-8 -*-
from concurrency.core import Http409
from concurrency.http import HttpResponseConflict


class Http409Middleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, Http409):
            return HttpResponseConflict()
