==================
Django Concurrency
==================


.. image:: https://secure.travis-ci.org/saxix/django-concurrency.png?branch=master
   :target: http://travis-ci.org/saxix/django-concurrency/


.. image:: https://coveralls.io/repos/saxix/django-concurrency/badge.png
   :target: https://coveralls.io/r/saxix/django-concurrency

.. image:: https://pypip.in/v/django-concurrency/badge.png
   :target: https://crate.io/packages/django-concurrency/

.. image:: https://pypip.in/d/django-concurrency/badge.png
   :target: https://crate.io/packages/django-concurrency/


django-concurrency is an optimistic locking library for Django 1.4.

It prevents users from doing concurrent editing in Django both from UI and from a
django command.



How it works
------------
sample code::

    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )

Now if you try::

    a = ConcurrentModel.objects.get(pk=1)
    b = ConcurrentModel.objects.get(pk=1)
    a.save()
    b.save()

you will get a ``RecordModifiedError`` on ``b.save()``

Links
~~~~~

   * Project home page: https://github.com/saxix/django-concurrency
   * Issue tracker: https://github.com/saxix/django-concurrency/issues?sort
   * Download: http://pypi.python.org/pypi/django-concurrency/
   * Docs: http://readthedocs.org/docs/django-concurrency/en/latest/


