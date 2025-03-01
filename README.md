Django Concurrency
==================


[![Pypi](https://badge.fury.io/py/django-concurrency.svg)](https://badge.fury.io/py/django-concurrency)
[![coverage](https://codecov.io/github/saxix/django-concurrency/coverage.svg?branch=develop)](https://codecov.io/github/saxix/django-concurrency?branch=develop)
[![Test](https://github.com/saxix/django-concurrency/actions/workflows/tests.yaml/badge.svg)](https://github.com/saxix/django-concurrency/actions/workflows/tests.yaml)
[![Docs](https://readthedocs.org/projects/django-concurrency/badge/?version=stable)](http://django-concurrency.readthedocs.io/en/stable/)
[![Django](https://img.shields.io/pypi/frameworkversions/django/django-concurrency)](https://pypi.org/project/django-concurrency/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/django-concurrency.svg)](https://pypi.org/project/django-concurrency/)


django-concurrency is an [optimistic lock][1] implementation for Django.

It prevents users from doing concurrent editing in Django both from UI and from a
django command.


How it works
------------

```python

from django.db import models
from concurrency.fields import IntegerVersionField

class ConcurrentModel( models.Model ):
    version = IntegerVersionField( )
    name = models.CharField(max_length=100)
```

Now if you try::

```python

a = ConcurrentModel.objects.get(pk=1)
a.name = '1'

b = ConcurrentModel.objects.get(pk=1)
b.name = '2'

a.save()
b.save()

```

you will get a ``RecordModifiedError`` on ``b.save()``


Similar projects
----------------

Other projects that handle concurrent editing are [django-optimistic-lock][10]
and [django-locking][11] anyway concurrency is "a batteries included" optimistic
lock management system, here some features not available elsewhere:

 * can be applied to any model; not only your code (ie. django.contrib.auth.Group)
 * handle [list-editable][2] ChangeList. (handle `#11313 <https://code.djangoproject.com/ticket/11313>`_)
 * manage concurrency conflicts in admin's actions
 * can intercept changes performend out of the django app (ie using pgAdmin, phpMyAdmin, Toads) (using [TriggerVersionField][6])
 * can be disabled if needed (see [disable_concurrency][3])
 * [ConditionalVersionField][4] to handle complex business rules



Project Links
------------

- Code: https://github.com/saxix/django-concurrency
- Documentation: https://django-concurrency.readthedocs.org/en/latest/
- Issue Tracker: https://github.com/saxix/django-concurrency/issues
- Download Package: http://pypi.python.org/pypi/django-concurrency/


[10]:https://github.com/gavinwahl/django-optimistic-lock
[11]:https://github.com/stdbrouw/django-locking
[1]:http://en.wikipedia.org/wiki/Optimistic_concurrency_control
[2]:https://django-concurrency.readthedocs.org/en/latest/admin.html#list-editable
[3]:https://django-concurrency.readthedocs.org/en/latest/api.html?#disable-concurrency
[4]:https://django-concurrency.readthedocs.org/en/latest/fields.html#conditionalversionfield
[6]:https://django-concurrency.readthedocs.org/en/latest/fields.html#triggerversionfield
