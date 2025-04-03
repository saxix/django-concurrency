from django.core.signals import got_request_exception
from django.urls.utils import get_callable

from concurrency.config import conf
from concurrency.exceptions import RecordModifiedError


class ConcurrencyMiddleware:
    """Intercept :ref:`RecordModifiedError` and invoke a callable defined in
    :setting:`CONCURRECY_HANDLER409` passing the request and the object.

    """

    def __init__(self, get_response=None) -> None:
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, RecordModifiedError):
            got_request_exception.send(sender=self, request=request)
            callback = get_callable(conf.HANDLER409)
            return callback(request, target=exception.target)
        return None
        # pragma: no cover
