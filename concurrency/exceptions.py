from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import DatabaseError


class VersionChangedError(ValidationError):
    pass


class RecordModifiedError(DatabaseError):
    def __init__(self, *args, **kwargs):
        self.target = kwargs.pop('target')
        super(RecordModifiedError, self).__init__(*args, **kwargs)


class InconsistencyError(DatabaseError):
    pass
