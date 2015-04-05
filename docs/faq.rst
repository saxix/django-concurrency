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



.. _2_protocols:

Why two protocols ?
-------------------

The initial implementation of |concurrency| used the real pattern [1]_,
but it required a partial rewrite of original Django's code and it was
very hard to maintain/keep updated, for this reason starting from version 0.3,
:ref:`select_for_update()` was used.

With the new  implementation (django 1.6) the optimistic lock pattern it
is easier to implement. Starting from version 0.7 |concurrency| uses different implementation
depending on the django version used.

.. note:: From 1.0 support for django < 1.6 will be dropped


.. seealso:: :setting:`USE_SELECT_FOR_UPDATE`

