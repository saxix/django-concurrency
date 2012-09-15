Django Concurrency
==================


.. image:: https://secure.travis-ci.org/saxix/django-concurrency.png?branch=master
   :target: http://travis-ci.org/saxix/django-concurrency/


django-concurrency is a optimistic locking library for Django 1.4.

It works adding a VersionField to the model, each time a model is successfully saved the VersionNumber is
incremented.


How it works
------------
sample code::

    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )

Now if if you try::

    a = ConcurrentModel.objects.get(pk=1)
    b = ConcurrentModel.objects.get(pk=1)
    a.save()
    b.save()

you will get a ``RecordModifedError`` on ``b.save()``

Links
~~~~~

   * Project home page: https://github.com/saxix/django-concurrency
   * Issue tracker: https://github.com/saxix/django-concurrency/issues?sort
   * Download: http://pypi.python.org/pypi/django-concurrency/
   * Docs: http://readthedocs.org/docs/django-concurrency/en/latest/


