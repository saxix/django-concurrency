# -*- coding: utf-8 -*-
from django.core.urlresolvers import get_callable
from concurrency.core import RecordModifiedError
from concurrency.views import handler409



# This middleware is still alpha and should not be used.
class ConcurrencyMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, RecordModifiedError):
            callback = get_callable(handler409)

            return callback(request, target=exception.target)
