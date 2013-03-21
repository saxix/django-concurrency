.. include:: globals.rst
.. _settings:

========
Settings
========

Available settings
==================

Here's a full list of all available settings, in alphabetical order, and their
default values.


.. setting:: CONCURRECY_SANITY_CHECK

CONCURRECY_SANITY_CHECK
-----------------------
.. versionadded:: 0.4

Default: ``True``

If you wand to disable the check raised when you try to save an object with a revision number set
but without pk (this should not happen) you can set ``CONCURRECY_SANITY_CHECK=False`` in your settings.

This is useful if you have some existing test code that use factories that creates a random number that
prevent the sanity check to pass


.. setting:: CONCURRENCY_FIELD_SIGNER


CONCURRENCY_FIELD_SIGNER
------------------------
.. versionadded:: 0.5

Default: ``concurrency.forms.VersionFieldSigner``

Default class used to sign the version numbers.



