==================
Django Concurrency
==================


.. image:: https://badge.fury.io/py/django-concurrency.svg
   :target: http://badge.fury.io/py/django-concurrency
   :alt: PyPI package


django-concurrency is an optimistic lock [1]_ implementation for Django.

Supported Django versions:

    - <=2.1.1  supports    1.11.x, 2.1.x, 2.2.x, 3.x
    - >=2.2    supports    3.x


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

.. |master-build| image:: https://secure.travis-ci.org/saxix/django-concurrency.svg?branch=master
                    :target: http://travis-ci.org/saxix/django-concurrency/

.. |master-cov| image:: https://codecov.io/gh/saxix/django-concurrency/branch/master/graph/badge.svg
                    :target: https://codecov.io/gh/saxix/django-concurrency

.. |master-doc| image:: https://readthedocs.org/projects/django-concurrency/badge/?version=stable
                    :target: http://django-concurrency.readthedocs.io/en/stable/

.. |dev-build| image:: https://secure.travis-ci.org/saxix/django-concurrency.svg?branch=develop
                  :target: http://travis-ci.org/saxix/django-concurrency/

.. |dev-cov| image:: https://codecov.io/gh/saxix/django-concurrency/branch/develop/graph/badge.svg
                    :target: https://codecov.io/gh/saxix/django-concurrency

.. |dev-doc| image:: https://readthedocs.org/projects/django-concurrency/badge/?version=stable
                    :target: http://django-concurrency.readthedocs.io/en/stable/



.. |wheel| image:: https://img.shields.io/pypi/wheel/django-concurrency.svg

_list-editable: https://django-concurrency.readthedocs.org/en/latest/admin.html#list-editable

.. _list-editable: https://django-concurrency.readthedocs.org/en/latest/admin.html#list-editable

.. _django-locking: https://github.com/stdbrouw/django-locking

.. _django-optimistic-lock: https://github.com/gavinwahl/django-optimistic-lock

.. _TriggerVersionField: https://django-concurrency.readthedocs.org/en/latest/fields.html#triggerversionfield

.. _ConditionalVersionField: https://django-concurrency.readthedocs.org/en/latest/fields.html#conditionalversionfield

.. _disable_concurrency: https://django-concurrency.readthedocs.org/en/latest/api.html?#disable-concurrency



.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/saxix/django-concurrency
   :target: https://gitter.im/saxix/django-concurrency?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. [1] http://en.wikipedia.org/wiki/Optimistic_concurrency_control
