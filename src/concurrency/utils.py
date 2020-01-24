import inspect
import logging
import warnings

from concurrency.exceptions import RecordModifiedError

logger = logging.getLogger(__name__)


def deprecated(replacement=None, version=None):
    """A decorator which can be used to mark functions as deprecated.
    replacement is a callable that will be called with the same args
    as the decorated function.
    >>> import pytest
    >>> @deprecated()
    ... def foo1(x):
    ...     return x
    ...
    >>> pytest.warns(DeprecationWarning, foo1, 1)
    1
    >>> def newfun(x):
    ...     return 0
    ...
    >>> @deprecated(newfun, '1.1')
    ... def foo2(x):
    ...     return x
    ...
    >>> pytest.warns(DeprecationWarning, foo2, 1)
    0
    >>>
    """

    def outer(oldfun):
        def inner(*args, **kwargs):
            msg = "%s is deprecated" % oldfun.__name__
            if version is not None:
                msg += "will be removed in version %s;" % version
            if replacement is not None:
                msg += "; use %s instead" % (replacement)
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            if callable(replacement):
                return replacement(*args, **kwargs)
            else:
                return oldfun(*args, **kwargs)

        return inner

    return outer


class ConcurrencyTestMixin(object):
    """
    Mixin class to test Models that use `VersionField`

    this class offer a simple test scenario. Its purpose is to discover
    some conflict in the `save()` inheritance::

        from concurrency.utils import ConcurrencyTestMixin
        from myproject.models import MyModel

        class MyModelTest(ConcurrencyTestMixin, TestCase):
            concurrency_model = TestModel0
            concurrency_kwargs = {'username': 'test'}

    """

    concurrency_model = None
    concurrency_kwargs = {}

    def _get_concurrency_target(self, **kwargs):
        # WARNING this method must be idempotent. ie must returns
        # always a fresh copy of the record
        args = dict(self.concurrency_kwargs)
        args.update(kwargs)
        return self.concurrency_model.objects.get_or_create(**args)[0]

    def test_concurrency_conflict(self):
        import concurrency.api as api

        target = self._get_concurrency_target()
        target_copy = self._get_concurrency_target()
        v1 = api.get_revision_of_object(target)
        v2 = api.get_revision_of_object(target_copy)
        assert v1 == v2, "got same row with different version (%s/%s)" % (v1, v2)
        target.save()
        assert target.pk is not None  # sanity check
        self.assertRaises(RecordModifiedError, target_copy.save)

    def test_concurrency_safety(self):
        import concurrency.api as api

        target = self.concurrency_model()
        version = api.get_revision_of_object(target)
        self.assertFalse(bool(version), "version is not null %s" % version)

    def test_concurrency_management(self):
        target = self.concurrency_model
        self.assertTrue(hasattr(target, '_concurrencymeta'),
                        "%s is not under concurrency management" % self.concurrency_model)

        revision_field = target._concurrencymeta.field

        self.assertTrue(revision_field in target._meta.fields,
                        "%s: version field not in meta.fields" % self.concurrency_model)


class ConcurrencyAdminTestMixin(object):
    pass


def refetch(model_instance):
    """
    Reload model instance from the database
    # """
    return model_instance.__class__.objects.get(pk=model_instance.pk)


def get_classname(o):
    """ Returns the classname of an object r a class

    :param o:
    :return:
    """
    if inspect.isclass(o):
        target = o
    elif callable(o):
        target = o
    else:
        target = o.__class__
    try:
        return target.__qualname__
    except AttributeError:  # pragma: no cover
        return target.__name__


def fqn(o):
    """Returns the fully qualified class name of an object or a class

    :param o: object or class
    :return: class name

    >>> import concurrency.fields
    >>> fqn('str')
    Traceback (most recent call last):
    ...
    ValueError: Invalid argument `str`
    >>> class A(object):
    ...     def method(self):
    ...         pass
    >>> str(fqn(A))
    'concurrency.utils.A'

    >>> str(fqn(A()))
    'concurrency.utils.A'

    >>> str(fqn(concurrency.fields))
    'concurrency.fields'

    >>> str(fqn(A.method))
    'concurrency.utils.A.method'


    """
    parts = []

    # if inspect.ismethod(o):
    #     try:
    #         cls = o.im_class
    #     except AttributeError:
    #         # Python 3 eliminates im_class, substitutes __module__ and
    #         # __qualname__ to provide similar information.
    #         parts = (o.__module__, o.__qualname__)
    #     else:
    #         parts = (fqn(cls), get_classname(o))
    if hasattr(o, '__module__'):
        parts.append(o.__module__)
        parts.append(get_classname(o))
    elif inspect.ismodule(o):
        return o.__name__
    if not parts:
        raise ValueError("Invalid argument `%s`" % o)
    return ".".join(parts)


def flatten(iterable):
    """
    flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    :param sequence: any object that implements iterable protocol (see: :ref:`typeiter`)
    :return: list

    Examples:

    >>> from adminactions.utils import flatten
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]

    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = list()
    for el in iterable:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return list(result)
