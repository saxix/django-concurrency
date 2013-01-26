.. include:: globals.rst

.. _api:

API
===

.. contents::
    :local:

RevisionMetaInfo
----------------

.. attribute:: field

ConcurrencyTestMixin
--------------------
.. autoclass:: concurrency.utils.ConcurrencyTestMixin


IntegerVersionField
-------------------
.. autoclass:: concurrency.fields.IntegerVersionField


AutoIncVersionField
-------------------
.. autoclass:: concurrency.fields.AutoIncVersionField

RawIntegerVersionField
-------------------
.. autoclass:: concurrency.fields.RawIntegerVersionField


RawAutoIncVersionField
-------------------
.. autoclass:: concurrency.fields.RawAutoIncVersionField

VersionField
------------
.. autoclass:: concurrency.forms.VersionField


ConcurrentForm
--------------
.. autoclass:: concurrency.forms.ConcurrentForm


VersionWidget
-------------
.. autoclass:: concurrency.forms.VersionWidget


.. _RecordModifiedError:

RecordModifiedError
-------------------
.. autoclass:: concurrency.core.RecordModifiedError


``concurrency_check``
---------------------

Sometimes, VersionField(s) are not ables to 'patch' the save() method,
(could happen if you mix metaclasses and abstract models,
or simply the order the fields are added to the your model) is where `concurrency_check` can be useful.
Simply call it in your `save()` method::

    from concurrency.core import concurrency_check

    def save(self, *args, **kwargs):
        concurrency_check(self, *args, **kwargs)
        logger.debug(u'Saving %s "%s".' % (self._meta.verbose_name, self))
        super(SecurityConcurrencyBaseModel, self).save(*args, **kwargs)
