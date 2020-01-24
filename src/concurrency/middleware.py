from django.core.signals import got_request_exception

from concurrency.config import conf
from concurrency.exceptions import RecordModifiedError

try:
    from django.urls.utils import get_callable
except ImportError:
    from django.core.urlresolvers import get_callable


class ConcurrencyMiddleware(object):
    """ Intercept :ref:`RecordModifiedError` and invoke a callable defined in
    :setting:`CONCURRECY_HANDLER409` passing the request and the object.

    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, RecordModifiedError):
            got_request_exception.send(sender=self, request=request)
            callback = get_callable(conf.HANDLER409)
            return callback(request, target=exception.target)
        else:  # pragma: no cover
            pass
