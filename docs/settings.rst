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

Handler invoked when a conflict is raised. The default implementation
simply raise :class:`RecordModifiedError <concurrency.exceptions.RecordModifiedError>`

Can be used to display the two version of the record and let the user to force
the update or merge the values.

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

Handler to intercept :class:`RecordModifiedError <concurrency.exceptions.RecordModifiedError>`
into :class:`ConcurrencyMiddleware <concurrency.middleware.ConcurrencyMiddleware>`.
The default implementation (:ref:`concurrency.views.conflict`) renders ``409.html``
while passing into the context the object that is going to be saved (``target``)

.. seealso:: :ref:`middleware`


.. setting:: CONCURRECY_MANUAL_TRIGGERS

MANUAL_TRIGGERS
---------------
.. versionadded:: 1.0

Default: ``False``

If false do not automatically create triggers, you can create them using :ref:`triggers`
 management command or manually using your DB client.



.. setting:: CONCURRENCY_POLICY

POLICY
------
.. versionchanged:: 0.7

Default: ``CONCURRENCY_LIST_EDITABLE_POLICY_SILENT``

.. _list_editable_policies:

.. setting:: CONCURRENCY_IGNORE_DEFAULT

IGNORE_DEFAULT
--------------
.. versionadded:: >1.2

Default: ``True``

Determines whether a default version number is ignored or used in a concurrency check.  While this
configuration defaults to True for backwards compatibility, this setting can cause omitted version
numbers to pass concurrency checks. New implementations are recommended to set this to ``False``.

.. note:: For security reasons, starting from version 1.5, default value will be ``False``.


``CONCURRENCY_LIST_EDITABLE_POLICY_SILENT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Used by admin's integrations to handle ``list_editable`` conflicts.
Do not save conflicting records, continue and save all non-conflicting records,
show a message to the user

``CONCURRENCY_LIST_EDITABLE_POLICY_ABORT_ALL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Used by admin's integations to handle ``list_editable``.
Stop at the first conflict and raise
:class:`RecordModifiedError <concurrency.exceptions.RecordModifiedError>`.
Note that if you want to use
:class:`ConcurrencyMiddleware <concurrency.middleware.ConcurrencyMiddleware>`
based conflict management you must set this flag.

.. seealso:: :ref:`list_editable`, :ref:`middleware`
