from __future__ import absolute_import, unicode_literals
import logging
from django.db.models.signals import class_prepared
from concurrency.core import _wrap_model_save

logger = logging.getLogger(__name__)

__all__ = []

#
#def class_prepared_concurrency_handler(sender, **kwargs):
#    if hasattr(sender, 'RevisionMetaInfo') and not (sender.RevisionMetaInfo.manually):
#        _wrap_model_save(sender)
#        from concurrency.api import get_version, get_object_with_version
#        setattr(sender._default_manager.__class__,
#                'get_object_with_version', get_object_with_version)
#        setattr(sender, 'get_concurrency_version', get_version)
#
#    else:
#        logger.debug('Skipped concurrency for %s' % sender)
#
#
#class_prepared.connect(class_prepared_concurrency_handler, dispatch_uid='class_prepared_concurrency_handler')
