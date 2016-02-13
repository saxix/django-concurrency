==================
Django Concurrency
==================


django-concurrency is an optimistic lock [1]_ implementation for Django.

Supported Django versions: 1.6.x, 1.7.x, 1.8.x, 1.9.

It prevents users from doing concurrent editing in Django both from UI and from a
django command.


How it works
------------
sample code::

    from django.db import models
    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )
        name = models.CharField(max_length=100)

Now if you try::

    a = ConcurrentModel.objects.get(pk=1)
    a.name = '1'

    b = ConcurrentModel.objects.get(pk=1)
    b.name = '2'

    a.save()
    b.save()

you will get a ``RecordModifiedError`` on ``b.save()``


Similar projects
----------------

Other projects that handle concurrent editing are `django-optimistic-lock`_ and `django-locking`_ anyway concurrency is "a batteries included" optimistic lock management system, here some features not available elsewhere:

 * can be applied to any model; not only your code (ie. django.contrib.auth.Group)
 * handle `list-editable`_ ChangeList. (handle `#11313 <https://code.djangoproject.com/ticket/11313>`_)
 * manage concurrency conflicts in admin's actions
 * can intercept changes performend out of the django app (ie using pgAdmin, phpMyAdmin, Toads) (using `TriggerVersionField`_)
 * can be disabled if needed (see `disable_concurrency`_)
 * `ConditionalVersionField`_ to handle complex business rules


Links
~~~~~

+--------------------+----------------+--------------+------------------------+
| Stable             | |master-build| | |master-cov| |                        |
+--------------------+----------------+--------------+------------------------+
| Development        | |dev-build|    | |dev-cov|    |                        |
+--------------------+----------------+--------------+------------------------+
| Project home page: |https://github.com/saxix/django-concurrency             |
+--------------------+---------------+----------------------------------------+
| Issue tracker:     |https://github.com/saxix/django-concurrency/issues?sort |
+--------------------+---------------+----------------------------------------+
| Download:          |http://pypi.python.org/pypi/django-concurrency/         |
+--------------------+---------------+----------------------------------------+
| Documentation:     |https://django-concurrency.readthedocs.org/en/latest/   |
+--------------------+---------------+--------------+-------------------------+

.. |master-build| image:: https://secure.travis-ci.org/saxix/django-concurrency.png?branch=master
                    :target: http://travis-ci.org/saxix/django-concurrency/

.. |master-cov| image:: https://coveralls.io/repos/saxix/django-concurrency/badge.svg?branch=master&service=github
            :target: https://coveralls.io/github/saxix/django-concurrency?branch=master


.. |dev-build| image:: https://secure.travis-ci.org/saxix/django-concurrency.png?branch=develop
                  :target: http://travis-ci.org/saxix/django-concurrency/

.. |dev-cov| image:: https://coveralls.io/repos/saxix/django-concurrency/badge.svg?branch=develop&service=github
        :target: https://coveralls.io/github/saxix/django-concurrency?branch=develop


.. |wheel| image:: https://pypip.in/wheel/blackhole/badge.png

_list-editable: https://django-concurrency.readthedocs.org/en/latest/admin.html#list-editable

.. _list-editable: https://django-concurrency.readthedocs.org/en/latest/admin.html#list-editable

.. _django-locking: https://github.com/stdbrouw/django-locking

.. _django-optimistic-lock: https://github.com/gavinwahl/django-optimistic-lock

.. _TriggerVersionField: https://django-concurrency.readthedocs.org/en/latest/fields.html#triggerversionfield

.. _ConditionalVersionField: https://django-concurrency.readthedocs.org/en/latest/fields.html#conditionalversionfield

.. _disable_concurrency: https://django-concurrency.readthedocs.org/en/latest/api.html?#disable-concurrency

.. [1] http://en.wikipedia.org/wiki/Optimistic_concurrency_control



.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/saxix/django-concurrency
   :target: https://gitter.im/saxix/django-concurrency?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
