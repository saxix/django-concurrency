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


.. setting:: CONCURRENCY_CALLBACK

CALLBACK
------------------------
.. versionadded:: 0.6

Default: None

Custom callable to handle conflicts

.. seealso:: :setting:`CONCURRENCY_POLICY`



.. setting:: CONCURRENCY_FIELD_SIGNER

FIELD_SIGNER
------------------------
.. versionadded:: 0.5

Default: ``concurrency.forms.VersionFieldSigner``

Class used to sign the version numbers.

.. seealso:: :ref:`Signining`



.. setting:: CONCURRENCY_HANDLER409

HANDLER409
-------------------------------
.. versionadded:: 0.6

Default: ``concurrency.views.conflict``

Handler to intercept :ref:`RecordModifiedError` into :ref:`concurrencymiddleware`.
The default implementation (:ref:`handler409`) renders ``409.html`` passing in the context the object that
is going to be saved (``target``) and the same object as stored in the database (``saved``)

.. seealso:: :ref:`middleware`


.. setting:: CONCURRENCY_POLICY

POLICY
-------------------------------
.. versionadded:: 0.6

Default: ``CONCURRENCY_POLICY_RAISE & CONCURRENCY_LIST_EDITABLE_POLICY_SILENT``

``CONCURRENCY_POLICY_RAISE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default behaviour. Raises :ref:`RecordModifiedError` as detects a conflict.

``CONCURRENCY_POLICY_CALLBACK``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Demand the conflict management to the callable defined in :setting:`CONCURRENCY_CALLBACK`

.. _list_editable_policies:

``CONCURRENCY_LIST_EDITABLE_POLICY_SILENT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Used by admin's integations to handle ``list_editable``.
Do not save conflite record, continue and save all no-coflict records,
show a message to the user

``CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Used by admin's integations to handle ``list_editable``.
Stop at the first conflict and raise :ref:`recordmodifiederror`. Note that if you want to use
:ref:`middleware` based conflict management you must set this flag.

.. seealso:: :ref:`list_editable`, :ref:`middleware`


.. setting:: CONCURRECY_SANITY_CHECK

SANITY_CHECK
-----------------------
.. versionadded:: 0.4

Default: ``True``

If you wand to disable the check raised when you try to save an object with a revision number set
but without pk (this should not happen) you can set ``CONCURRECY_SANITY_CHECK=False`` in your settings.

This is useful if you have some existing test code that use factories that creates a random number that
prevent the sanity check to pass

