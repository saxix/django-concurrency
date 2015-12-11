from __future__ import absolute_import, unicode_literals

from django.core.exceptions import SuspiciousOperation, ValidationError
from django.db import DatabaseError
from django.utils.translation import ugettext as _


class VersionChangedError(ValidationError):
    pass


class RecordModifiedError(DatabaseError):
    def __init__(self, *args, **kwargs):
        self.target = kwargs.pop('target')
        super(RecordModifiedError, self).__init__(*args, **kwargs)


class VersionError(SuspiciousOperation):

    def __init__(self, message=None, code=None, params=None, *args, **kwargs):
        self.message = message or _("Version number is missing or has been tampered with")
