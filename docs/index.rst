.. |concurrency| replace:: Concurrency
.. |version| replace:: 0.1

.. _index:

Documentation
=============

**django-concurrency is a optimistic locking library for Django Models**.

It's pure python code do not depend on any specific database backend

How it works
------------
sample code::

    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )

Now if if you try (fake code) ::

    a = ConcurrentModel.objects.get(pk=1)
    b = ConcurrentModel.objects.get(pk=1)
    a.save()
    b.save()

you will get a ``RecordModifedError`` on ``b.save()``


.. toctree::
    :maxdepth: 1

    help
    api

