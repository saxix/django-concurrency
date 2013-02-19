.. include:: globals.rst

.. _api:

API
===

.. contents::
    :local:


IntegerVersionField
-------------------
.. autoclass:: concurrency.fields.IntegerVersionField


AutoIncVersionField
-------------------
.. autoclass:: concurrency.fields.AutoIncVersionField

.. _concurrentform:

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

.. _concurrency_check:

``concurrency_check()``
------------------------

Sometimes, VersionField(s) cannot wraps the save() method,
is these cirumstances you can check it manually ::

    from concurrency.core import concurrency_check

    class AbstractModelWithCustomSave(models.Model):
        version = IntegerVersionField(db_column='cm_version_id', manually=True)

    def save(self, *args, **kwargs):
        concurrency_check(self, *args, **kwargs)
        super(SecurityConcurrencyBaseModel, self).save(*args, **kwargs)

.. note:: Please note ``manually=True`` argument in `IntegerVersionField()` definition


.. _apply_concurrency_check:

``apply_concurrency_check()``
------------------------------
.. versionadded:: 0.4

Add concurrency check to existing classes.

.. autofunction:: concurrency.core.apply_concurrency_check


.. _ConcurrencyTestMixin:

ConcurrencyTestMixin
--------------------
.. autoclass:: concurrency.utils.ConcurrencyTestMixin



.. _CONCURRECY_SANITY_CHECK:

CONCURRECY_SANITY_CHECK
-----------------------

If you wand to disable the check raised when you try to save an object with a revision number set
but without pk (this should not happen) you can set ``CONCURRECY_SANITY_CHECK=False`` in your settings.

This is useful if you have some existing test code that use factories that create a random number that
prevent the sanity check to pass

