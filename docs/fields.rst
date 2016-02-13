.. include:: globals.txt

.. _fields:

Fields
======

.. contents::
    :local:

.. _concurrency.fields.VersionField:

VersionField
------------
.. autoclass:: concurrency.fields.VersionField


IntegerVersionField
-------------------
.. autoclass:: concurrency.fields.IntegerVersionField


AutoIncVersionField
-------------------
.. autoclass:: concurrency.fields.AutoIncVersionField


.. _concurrency.fields.TriggerVersionField:


TriggerVersionField
-------------------
.. class:: concurrency.fields.TriggerVersionField


This field use a database trigger to update the version field.
Using this you can control external updates (ie using tools like phpMyAdmin, pgAdmin, SQLDeveloper).
The trigger is automatically created during ``syncdb()``
or you can use the :ref:`triggers` management command.

.. versionchanged:: 1.0

.. warning:: Before |concurrency| 1.0 two triggers per field were created,
if you are upgrading you must manually remove old triggers and recreate them
using :ref:`triggers`_ management command

`trigger_name`
~~~~~~~~~~~~~~

.. versionadded:: 1.0

.. attribute:: TriggerVersionField.trigger_name

Starting from 1.0 you can customize the name of the trigger created.
Otherwise for each `TriggerVersionField` will be created two triggers named:


.. code-block:: python

        'concurrency_[DBTABLENAME]_[FIELDNAME]'

.. warning:: Any name will be automatically prefixed with ``concurrency_``


.. _triggers:

`triggers` management command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. command:: triggers

Helper command to work with triggers:

    * ``list``   : list existing triggers for each database

    * ``drop``   : drop exisitng triggers

    * ``create`` : create required triggers

example

.. code-block:: bash

    sax@: (concurrency) django-concurrency [feature/triggers*] $ ./demo/manage.py triggers create
    DATABASE             TRIGGERS
    default              concurrency_concurrency_triggerconcurrentmodel_u


.. _concurrency.fields.ConditionalVersionField:


ConditionalVersionField
-----------------------

.. versionadded:: 1.1


This field allow to configure which fields trigger the version increment so to limit
the scope of the concurrency checks.

.. code-block:: python

    class User(models.Model):
        version = ConditionalVersionField()
        username = models.CharField(...)
        password = models.PasswordField(...)

        class ConcurrencyMeta:
            check_fields = ('username',)


