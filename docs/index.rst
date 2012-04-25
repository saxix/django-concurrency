.. |concurrency| replace:: Concurren cy
.. |pkg| replace:: dja
.. |version| replace:: 0.1

.. _index:

Documentation
=============

**django-concurrency is a optimistic locking library for Django Models**.

It's pure python code do not depend on any specific database backend

How it works
=================

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


Table Of Contents
=================

.. toctree::
    :maxdepth: 1

    help
    api

Links
~~~~~

   * Project home page: https://github.com/saxix/django-iadmin
   * Issue tracker: https://github.com/saxix/django-iadmin/issues?sort
   * Download: http://pypi.python.org/pypi/django-iadmin/
   * Docs: http://readthedocs.org/docs/django-iadmin/en/latest/


