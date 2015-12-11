.. include:: globals.txt
.. _faq:


===
FAQ
===

.. contents::
   :local:

.. _update_fields:

How is managed `update_fields`
------------------------------

It is possible to use `save(update_fields=...)` parameter without interfree with
the concurrency check algorithm

.. code-block:: python

    x1 = MyModel.objects.create(name='abc')
    x2 = MyModel.objects.get(pk=x1.pk)

    x1.save()
    x2.save(update_fields=['username'])  # raise RecordModifiedError

anyway this will NOT raise any error

.. code-block:: python

    x1 = MyModel.objects.create(name='abc')
    x2 = MyModel.objects.get(pk=x1.pk)

    x1.save(update_fields=['username'])  # skip update version number
    x2.save()  # saved


.. note:: `TriggerVersionField` will be always updated


