from django.core.exceptions import SuspiciousOperation, ValidationError
from django.db import DatabaseError
from django.utils.translation import gettext as _


class VersionChangedError(ValidationError):
    pass


class RecordModifiedError(DatabaseError):
    def __init__(self, *args, **kwargs) -> None:
        self.target = kwargs.pop("target")
        super().__init__(*args, **kwargs)


class VersionError(SuspiciousOperation):
    def __init__(self, message=None, code=None, params=None, *args, **kwargs) -> None:
        self.message = message or _("Version number is missing or has been tampered with")
