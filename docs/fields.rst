.. include:: globals.txt

.. _fields:

Fields
======

.. contents::
    :local:

VersionField
------------
.. autoclass:: concurrency.fields.VersionField


IntegerVersionField
-------------------
.. autoclass:: concurrency.fields.IntegerVersionField


AutoIncVersionField
-------------------
.. autoclass:: concurrency.fields.AutoIncVersionField



TriggerVersionField
-------------------
.. class:: concurrency.fields.TriggerVersionField

This field use a database trigger to update the version field.
Using this you can control external updates (ie using tools like phpMyAdmin, pgAdmin, SQLDeveloper).
The trigger is automatically created during ``syncdb()`` or you can use the :ref:`triggers` management command.

.. note:: if you get ``TriggerVersionField need concurrency database backend`` error, it
            means that you are using a ``django.db.backends.XY`` backend instead of
            ``concurrency.db.backends.XY`` or that your database is not supported.

.. note:: ``concurrency.db.backends.XY`` inheriths from ``django.db.backends.XY``,
            simply add the ability to create/manipulate triggers, no changes to original code.


``triggers`` management command
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To easy work with |concurrency| created database triggers new command ``triggers`` is provided.
It can:

    * ``list``   : list existing triggers for each database

    * ``drop``   : drop exisitng triggers

    * ``create`` : create required triggers

example

.. code-block:: bash

    sax@: (concurrency) django-concurrency [feature/triggers*] $ ./demo/manage.py triggers create
    DATABASE             TRIGGERS
    default              concurrency_concurrency_triggerconcurrentmodel_u
