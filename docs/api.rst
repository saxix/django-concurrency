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

.. class:: concurrency.exceptions.RecordModifiedError

RecordModifiedError
-------------------
.. autoclass:: concurrency.exceptions.RecordModifiedError



.. _InconsistencyError:

InconsistencyError
------------------
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
--------------------
.. autoclass:: concurrency.admin.ConcurrentModelAdmin

.. _ConcurrencyActionMixin:

ConcurrencyActionMixin
----------------------
.. autoclass:: concurrency.admin.ConcurrencyActionMixin


.. _ConcurrencyListEditableMixin:

ConcurrencyListEditableMixin
----------------------------
.. autoclass:: concurrency.admin.ConcurrencyListEditableMixin


----------
Middleware
----------

.. _concurrencymiddleware:
.. class:: concurrency.middleware.ConcurrencyMiddleware

ConcurrencyMiddleware
---------------------
.. seealso:: :ref:`middleware`

.. autoclass:: concurrency.middleware.ConcurrencyMiddleware


.. _handler409:

concurrency.views.conflict
--------------------------
.. autofunction:: concurrency.views.conflict



-------
Helpers
-------


.. _apply_concurrency_check:

`apply_concurrency_check()`
---------------------------

.. versionadded:: 0.4

.. versionchanged:: 0.8

Add concurrency check to existing classes.

.. note:: With Django 1.7 and the new migrations management, this utility does
  not work anymore. To add concurrency management to a external Model,
  you need to use a migration to add a `VersionField` to the desired Model.


.. note:: See ``demo.auth_migrations`` for a example how to add
:class:`IntegerVersionField <concurrency.fields.IntegerVersionField>` to :class:`auth.Group` )

.. code-block:: python

    operations = [
        # add version to django.contrib.auth.Group
        migrations.AddField(
            model_name='Group',
            name='version',
            field=IntegerVersionField(help_text=b'Version', default=1),
        ),
    ]

and put in your settings.py

.. code-block:: python

        MIGRATION_MODULES = {
            ...
            ...
            'auth': '<new.migration.package>',
        }


.. _disable_concurrency:

`disable_concurrency()`
-----------------------

.. versionadded:: 0.6


Context manager to temporary disable concurrency checking.


.. versionchanged:: 0.9

Starting from version 0.9, `disable_concurrency` can disable both at Model
level or instance level, depending on the passed object.
Passing Model is useful in django commands, load data or fixtures,
where instance should be used by default


.. versionchanged:: 1.0

Is now possible use `disable_concurrency` without any argument to disable
concurrency on any Model.
This features has been developed to be used in django commands


.. versionchanged:: 1.1

Does not raise an exception if a model not under concurrency management is passed as argument.

examples
~~~~~~~~

.. code-block:: python

    @disable_concurrency()
    def recover_view(self, request, version_id, extra_context=None):
        return super(ReversionConcurrentModelAdmin, self).recover_view(request,
                                                            version_id,
                                                            extra_context)


.. code-block:: python

    def test_recover():
        deleted_list = revisions.get_deleted(ReversionConcurrentModel)
        delete_version = deleted_list.get(id=5)

        with disable_concurrency(ReversionConcurrentModel):
            deleted_version.revert()


`concurrency_disable_increment()`
---------------------------------

.. versionadded:: 1.1


Context manager to temporary disable version increment.
Concurrent save is still checked but no version increment is triggered,
this creates 'shadow saves',

It accepts both a Model or an instance as target.



------------
Templatetags
------------


.. templatefilter:: identity

`identity`
----------
.. autofunction:: concurrency.templatetags.concurrency.identity


.. templatefilter:: version

`version`
---------
.. autofunction:: concurrency.templatetags.concurrency.version



.. templatefilter:: is_version

`is_version`
------------
.. autofunction:: concurrency.templatetags.concurrency.is_version



-------------
Test Utilties
-------------

.. _concurrencytestmixin:

ConcurrencyTestMixin
--------------------
.. autoclass:: concurrency.utils.ConcurrencyTestMixin




.. _signining:

---------
Signining
---------

.. versionadded:: 0.5

:ref:`concurrency.fields.VersionField` is 'displayed' in the Form using an :class:`django.forms.HiddenInput` widget, anyway to be sure that the version is not
tampered with, its value is `signed`. The default VersionSigner is :class:`concurrency.forms.VersionFieldSigner` that simply
extends :class:`django.core.signing.Signer`. If you want change your Signer you can set :setting:`CONCURRENCY_FIELD_SIGNER` in your settings

    :file:`mysigner.py` ::

        class DummySigner():
            """ Dummy signer that simply returns the raw version value. (Simply do not sign it) """
            def sign(self, value):
                return smart_str(value)

            def unsign(self, signed_value):
                return smart_str(signed_value)

    :file:`settings.py` ::

        CONCURRENCY_FIELD_SIGNER = "myapp.mysigner.DummySigner"

