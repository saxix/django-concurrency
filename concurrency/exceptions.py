from django.core.exceptions import ValidationError, SuspiciousOperation
from django.utils.translation import ugettext as _
from django.db import DatabaseError


class VersionChangedError(ValidationError):
    pass


class RecordModifiedError(DatabaseError):
    def __init__(self, *args, **kwargs):
        self.target = kwargs.pop('target')
        super(RecordModifiedError, self).__init__(*args, **kwargs)


class InconsistencyError(DatabaseError):
    pass


class VersionError(SuspiciousOperation):
    def __init__(self, message=None, code=None, params=None):
        self.message = message or _("Version number is missing or has been tampered with")
