from django.db import models, router, transaction
from django.db.models import signals
from datetime import datetime
import logging
from django.utils.functional import curry
from django.db.models import IntegerField
from django.db.models.fields import DateTimeField, AutoField
from django.db import DatabaseError
from django.utils.timezone import utc

logger = logging.getLogger('concurrency')

class RecordModifiedError(DatabaseError):
    pass


class ConcurrentModelManager(models.Manager):
    def get_or_create(self, **kwargs):
        if 'pk' in kwargs:
            pass
        else:
            super(ConcurrentModelManager).get_or_create(**kwargs)


def lookup_revision(cls):
    for c, fk in cls._meta.parents.items():
        if hasattr(c, 'RevisionMetaInfo'):
            return c.RevisionMetaInfo.field, c
    if hasattr(cls, 'RevisionMetaInfo'):
        return cls.RevisionMetaInfo.field, cls
    return None, None


def save_base(self, raw=False, cls=None, origin=None, force_insert=False,
              force_update=False, using=None):
    """
    Does the heavy-lifting involved in saving. Subclasses shouldn't need to
    override this method. It's separate from save() in order to hide the
    need for overrides of save() to pass around internal-only parameters
    ('raw', 'cls', and 'origin').
    """
    using = using or router.db_for_write(self.__class__, instance=self)
    assert not (force_insert and force_update)
    if cls is None:
        cls = self.__class__
        meta = cls._meta
        if not meta.proxy:
            origin = cls
    else:
        meta = cls._meta

    if origin and not meta.auto_created:
        signals.pre_save.send(sender=origin, instance=self, raw=raw, using=using)

    # If we are in a raw save, save the object exactly as presented.
    # That means that we don't try to be smart about saving attributes
    # that might have come from the parent class - we just save the
    # attributes we have been given to the class we have been given.
    # We also go through this process to defer the save of proxy objects
    # to their actual underlying model.
    if not raw or meta.proxy:
        if meta.proxy:
            org = cls
        else:
            org = None
        for parent, field in meta.parents.items():
            # At this point, parent's primary key field may be unknown
            # (for example, from administration form which doesn't fill
            # this field). If so, fill it.
            if field and getattr(self, parent._meta.pk.attname) is None and getattr(self,
                field.attname) is not None:
                setattr(self, parent._meta.pk.attname, getattr(self, field.attname))

            self.save_base(cls=parent, origin=org, using=using)

            if field:
                setattr(self, field.attname, self._get_pk_val(parent._meta))
        if meta.proxy:
            return
            # concurrency code
    versionField, versionClass = lookup_revision(cls)
    currentVersion = self._get_revision_number()
    newVersion = cls is versionClass and self._revision_get_next() or currentVersion
    logger.debug('[%s] old version number: %s', cls.__name__, currentVersion)
    logger.debug('[%s] new version number: %s', cls.__name__, newVersion)
    # .concurrency code

    if not meta.proxy:
        non_pks = [f for f in meta.local_fields if not f.primary_key]

        # First, try an UPDATE. If that doesn't update anything, do an INSERT.
        pk_val = self._get_pk_val(meta)
        pk_set = pk_val is not None
        record_exists = True
        manager = cls._base_manager

        if pk_set:
            # Determine whether a record with the primary key already exists.
            if (force_update or (not force_insert and manager.using(using).filter(pk=pk_val).exists())):
                # It does already exist, so do an UPDATE.
                if force_update or non_pks:
                    values = [(f, None, (raw and getattr(self, f.attname) or f.pre_save(self, False))) for f in
                                                                                                       non_pks]
                    # concurrency code
                    if cls is versionClass:
                        versionField = cls.RevisionMetaInfo.field
                        values.append([versionField, None, newVersion])
                        d = {"pk": pk_val, cls.RevisionMetaInfo.field.name: currentVersion}
                        rows = manager.filter(**d)._update(values)
                    else:
                        rows = manager.filter(pk=pk_val)._update(values)
                    logger.debug('[%s] rows: %s', cls.__name__, rows)

                    if rows == 0:
                        rows = manager.filter(pk=pk_val)
                        if rows:
                            raise RecordModifiedError("Record changed....")
                    else:
                        self._set_revision_number(newVersion)
                    if force_update and not rows:
                        raise DatabaseError("Forced update did not affect any rows.")
                        # .concurrency code

            else:
                record_exists = False
        if not pk_set or not record_exists:
            if meta.order_with_respect_to:
                # If this is a model with an order_with_respect_to
                # autopopulate the _order field
                field = meta.order_with_respect_to
                order_value = manager.using(using).filter(**{field.name: getattr(self, field.attname)}).count()
                self._order = order_value

            fields = meta.local_fields
            if not pk_set:
                if force_update:
                    raise DatabaseError("Cannot force an update in save() with no primary key.")
                fields = [f for f in fields if not isinstance(f, AutoField)]

            record_exists = False
            self._set_revision_number(newVersion)
            update_pk = bool(meta.has_auto_field and not pk_set)
            result = manager._insert([self], fields=fields, return_id=update_pk, using=using, raw=raw)

            if update_pk:
                setattr(self, meta.pk.attname, result)
        transaction.commit_unless_managed(using=using)

    # Store the database on which the object was saved
    self._state.db = using
    # Once saved, this is no longer a to-be-added instance.
    self._state.adding = False

    # Signal that the save is complete
    if origin and not meta.auto_created:
        signals.post_save.send(sender=origin, instance=self,
            created=(not record_exists), raw=raw, using=using)


save_base.alters_data = True

