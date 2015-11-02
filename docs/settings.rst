.. include:: globals.txt
.. _settings:

========
Settings
========

Available settings
==================

Here's a full list of all available settings, in alphabetical order, and their
default values.

.. note:: Each entry **MUST** have the prefix ``CONCURRENCY_`` when used in your settings.py


.. setting:: CONCURRENCY_ENABLED

ENABLED
-------
.. versionadded:: 0.10

Default: ``True``

enable/disable concurrency


.. setting:: CONCURRENCY_CALLBACK

CALLBACK
--------
.. versionchanged:: 0.7

Default: ``concurrency.views.callback``

Handler invoked used to manage concurrent editing. The default implementation
simply raise :ref:`RecordModifiedError`



.. setting:: CONCURRENCY_FIELD_SIGNER

FIELD_SIGNER
------------
.. versionadded:: 0.5

Default: ``concurrency.forms.VersionFieldSigner``

Class used to sign the version numbers.

.. seealso:: :ref:`Signining`



.. setting:: CONCURRENCY_HANDLER409

HANDLER409
----------
.. versionadded:: 0.6

Default: ``concurrency.views.conflict``

Handler to intercept :ref:`RecordModifiedError` into :ref:`concurrencymiddleware`.
The default implementation (:ref:`handler409`) renders ``409.html`` while passing into the context the object that
is going to be saved (``target``) and the same object as stored in the database (``saved``)

.. seealso:: :ref:`middleware`


.. setting:: CONCURRENCY_POLICY

POLICY
------
.. versionchanged:: 0.7

Default: ``CONCURRENCY_LIST_EDITABLE_POLICY_SILENT``

.. _list_editable_policies:

``CONCURRENCY_LIST_EDITABLE_POLICY_SILENT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Used by admin's integrations to handle ``list_editable`` conflicts.
Do not save conflicting records, continue and save all non-conflicting records,
show a message to the user

``CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Used by admin's integations to handle ``list_editable``.
Stop at the first conflict and raise :ref:`recordmodifiederror`. Note that if you want to use
:ref:`middleware` based conflict management you must set this flag.

.. seealso:: :ref:`list_editable`, :ref:`middleware`


.. setting:: CONCURRECY_SANITY_CHECK

SANITY_CHECK
------------
.. versionchanged:: 0.7

Default: ``False``

Deprecated. Starting from 0.7 has no effect and will be removed in 0.8


.. setting:: USE_SELECT_FOR_UPDATE
