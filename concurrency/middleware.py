# -*- coding: utf-8 -*-
from django.core.signals import got_request_exception
from django.core.urlresolvers import get_callable
from concurrency.core import RecordModifiedError
from concurrency.views import handler409


class ConcurrencyMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, RecordModifiedError):
            got_request_exception.send(sender=self, request=request)
            callback = get_callable(handler409)
            return callback(request, target=exception.target)
