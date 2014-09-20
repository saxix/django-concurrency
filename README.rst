==================
Django Concurrency
==================


.. image:: https://pypip.in/v/django-concurrency/badge.png
      :target: https://crate.io/packages/django-concurrency/

.. image:: https://pypip.in/d/django-concurrency/badge.png
       :target: https://crate.io/packages/django-concurrency/


django-concurrency is an optimistic lock [1]_ implementation for Django.

Tested with: 1.4.x, 1.5.x, 1.6.x, 1.7 trunk.

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


Similar projects
----------------

Other projects that handle concurrent editing are `django-optimistic-lock`_ and `django-locking`_ anyway concurrency is "a batteries included" optimistic lock management system, here some features not available elsewhere:

 * can be applied to any model; not only your code (ie. django.contrib.auth.Group)
 * works with django 1.4 and 1.5
 * handle `list-editable`_ ChangeList. (handle `#11313 <https://code.djangoproject.com/ticket/11313>`_)
 * manage concurrency conflicts in admin's actions
 * can intercept changes performend out of the django app (ie using pgAdmin, phpMyAdmin, Toads) (using `TriggerVersionField_`


Links
~~~~~

+--------------------+----------------+--------------+------------------------+
| Stable             | |master-build| | |master-cov| | |master-req|           |
+--------------------+----------------+--------------+------------------------+
| Development        | |dev-build|    | |dev-cov|    | |dev-req|              |
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

.. |master-cov| image:: https://coveralls.io/repos/saxix/django-concurrency/badge.png?branch=master
                    :target: https://coveralls.io/r/saxix/django-concurrency

.. |master-req| image:: https://requires.io/github/saxix/django-concurrency/requirements.png?branch=master
                    :target: https://requires.io/github/saxix/django-concurrency/requirements/?branch=master
                    :alt: Requirements Status


.. |dev-build| image:: https://secure.travis-ci.org/saxix/django-concurrency.png?branch=develop
                  :target: http://travis-ci.org/saxix/django-concurrency/

.. |dev-cov| image:: https://coveralls.io/repos/saxix/django-concurrency/badge.png?branch=develop
                :target: https://coveralls.io/r/saxix/django-concurrency

.. |dev-req| image:: https://requires.io/github/saxix/django-concurrency/requirements.png?branch=develop
                    :target: https://requires.io/github/saxix/django-concurrency/requirements/?branch=develop
                    :alt: Requirements Status

.. |wheel| image:: https://pypip.in/wheel/blackhole/badge.png

_list-editable: https://django-concurrency.readthedocs.org/en/latest/admin.html#list-editable

.. _list-editable: https://django-concurrency.readthedocs.org/en/latest/admin.html#list-editable

.. _django-locking: https://github.com/stdbrouw/django-locking

.. _django-optimistic-lock: https://github.com/gavinwahl/django-optimistic-lock

.. _TriggerVersionField: https://django-concurrency.readthedocs.org/en/latest/fields.html#triggerversionfield

.. [1] http://en.wikipedia.org/wiki/Optimistic_concurrency_control

