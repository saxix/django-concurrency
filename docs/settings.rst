.. include:: globals.rst
.. _settings:

========
Settings
========

Available settings
==================

Here's a full list of all available settings, in alphabetical order, and their
default values.

.. note:: Each entry **MUST** have the prefix ``CONCURRENCY_`` when used in your settings.py

.. setting:: CONCURRENCY_FIELD_SIGNER


.. _concurrency_field_signer:

FIELD_SIGNER
------------------------

.. versionadded:: 0.5
.. seealso:: :ref:`Signining`

Default: ``concurrency.forms.VersionFieldSigner``


Default class used to sign the version numbers.


.. setting:: CONCURRECY_HANDLER409

HANDLER409
-------------------------------
.. versionadded:: 0.6
.. seealso:: :ref:`middleware`

Default: ``concurrency.views.conflict``

Handler to intercept :ref:`RecordModifiedError` into :ref:`concurrencymiddleware`.
The default implementation (:ref:`handler409`) renders ``409.html`` passing in the context the object that
is going to be saved (``target``) and the same object as stored in the database (``saved``)



.. setting:: CONCURRECY_LIST_EDITABLE_POLICY

LIST_EDITABLE_POLICY
-------------------------------
.. versionadded:: 0.6

How to manage concurrency errors in `list_editable` updates:

    ``concurrency.config.CONCURRENCY_LIST_EDITABLE_POLICY_SILENT``

    do not save current records, save others, show message to the user

    ``concurrency.config.CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL``

    abort whole transaction



.. setting:: CONCURRECY_SANITY_CHECK

SANITY_CHECK
-----------------------
.. versionadded:: 0.4

Default: ``True``

If you wand to disable the check raised when you try to save an object with a revision number set
but without pk (this should not happen) you can set ``CONCURRECY_SANITY_CHECK=False`` in your settings.

This is useful if you have some existing test code that use factories that creates a random number that
prevent the sanity check to pass

