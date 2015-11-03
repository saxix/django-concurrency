# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.signals import got_request_exception
from django.core.urlresolvers import get_callable

from concurrency.config import conf
from concurrency.exceptions import RecordModifiedError


class ConcurrencyMiddleware(object):
    """ Intercept :ref:`RecordModifiedError` and invoke a callable defined in
    :setting:`CONCURRECY_HANDLER409` passing the request and the object.

    """

    def process_exception(self, request, exception):
        if isinstance(exception, RecordModifiedError):
            got_request_exception.send(sender=self, request=request)
            callback = get_callable(conf.HANDLER409)
            return callback(request, target=exception.target)
