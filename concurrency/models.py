import logging
from django.db.models.signals import class_prepared
from concurrency.core import _wrap_model_save

logger = logging.getLogger('concurrency')

__all__ = []


def class_prepared_concurrency_handler(sender, **kwargs):
    if hasattr(sender, 'RevisionMetaInfo') and not (sender.RevisionMetaInfo.manually):
        _wrap_model_save(sender)
    else:
        logger.debug('Skipped concurrency for %s' % sender)


class_prepared.connect(class_prepared_concurrency_handler, dispatch_uid='class_prepared_concurrency_handler')
