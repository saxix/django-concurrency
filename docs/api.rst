.. include:: globals.txt

.. _api:

API
===

.. contents::
    :local:

-----
Forms
-----

.. _concurrentform:

ConcurrentForm
--------------
.. autoclass:: concurrency.forms.ConcurrentForm


VersionWidget
-------------
.. autoclass:: concurrency.forms.VersionWidget



----------
Exceptions
----------

.. _VersionChangedError:

VersionChangedError
-------------------
.. autoclass:: concurrency.exceptions.VersionChangedError



.. _RecordModifiedError:

RecordModifiedError
-------------------
.. autoclass:: concurrency.exceptions.RecordModifiedError



.. _InconsistencyError:

InconsistencyError
-------------------
.. versionchanged:: 0.7
.. warning:: removed in 0.7
.. class:: concurrency.exceptions.InconsistencyError


.. _VersionError:

VersionError
-------------------
.. autoclass:: concurrency.exceptions.VersionError



-----
Admin
-----

.. _ConcurrentModelAdmin:

ConcurrentModelAdmin
---------------------
.. autoclass:: concurrency.admin.ConcurrentModelAdmin

.. _ConcurrencyActionMixin:

ConcurrencyActionMixin
----------------------
.. autoclass:: concurrency.admin.ConcurrencyActionMixin


.. _ConcurrencyListEditableMixin:

ConcurrencyListEditableMixin
-----------------------------
.. autoclass:: concurrency.admin.ConcurrencyListEditableMixin


-----------
Middleware
-----------

.. _concurrencymiddleware:

ConcurrencyMiddleware
----------------------
.. seealso:: :ref:`middleware`

.. autoclass:: concurrency.middleware.ConcurrencyMiddleware


.. _handler409:

``concurrency.views.conflict()``
---------------------------------
.. autoclass:: concurrency.views.conflict



--------
Helpers
--------

.. _concurrency_check:

``concurrency_check()``
------------------------

Sometimes, VersionField(s) cannot wrap the save() method,
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

.. versionchanged:: 0.8

Add concurrency check to existing classes.

.. autofunction:: concurrency.api.apply_concurrency_check


.. note:: With Django 1.7 and the new migrations management, this utility does
  not work anymore. To add concurrency management to a external Model,
  you need to use a migration to add a `VersionField` to the desired Model.


.. note:: See ``tests.auth_migrations`` for a example how to add ``IntegerVersionField``
  to ``auth.Permission``)


.. _disable_concurrency:

``disable_concurrency()``
--------------------------
.. versionadded:: 0.6

Context manager to temporary disable concurrency checking.

.. versionchanged:: 0.9

Starting from version 0.9, `disable_concurrency` can disable both at Model level or instance level, depending on the
passed object.
Passing Model is useful in django commands, loadin data or fixtures, where instance should be used by default


.. _disable_sanity_check:

``disable_sanity_check()``
--------------------------
.. versionadded:: 0.6

Context manager to disable sanity check checking for one model. see :ref:`import_data`


------------
Templatetags
------------


.. templatefilter:: identity

``identity``
------------
.. autofunction:: concurrency.templatetags.concurrency.identity


.. templatefilter:: version

``version``
------------
.. autofunction:: concurrency.templatetags.concurrency.version



.. templatefilter:: is_version

``is_version``
---------------
.. autofunction:: concurrency.templatetags.concurrency.is_version



---------------------
Test Utilties
---------------------

.. _concurrencytestmixin:

ConcurrencyTestMixin
---------------------
.. autoclass:: concurrency.utils.ConcurrencyTestMixin




.. _signining:

---------------------
Signining
---------------------
.. versionadded:: 0.5

``VersionField`` is 'displayed' in the Form using an ``HiddenInput`` widget, anyway to be sure that the version is not
tampered with, its value is `signed`. The default VersionSigner is ``concurrency.forms.VersionFieldSigner`` that simply
extends ``django.core.signing.Signer``. If you want change your Signer you can set :setting:`CONCURRENCY_FIELD_SIGNER` in your settings

    :file:`mysigner.py` ::

        class DummySigner():
            """ Dummy signer that simply returns the raw version value. (Simply do not sign it) """
            def sign(self, value):
                return smart_str(value)

            def unsign(self, signed_value):
                return smart_str(signed_value)

    :file:`settings.py` ::

        CONCURRENCY_FIELD_SIGNER = "myapp.mysigner.DummySigner"

