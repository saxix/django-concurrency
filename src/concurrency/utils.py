import inspect
import logging
import warnings

logger = logging.getLogger(__name__)


def deprecated(replacement=None, version=None):
    """Mark function as deprecated.

    replacement is a callable that will be called with the same args
    as the decorated function.
    >>> import pytest
    >>> @deprecated()
    ... def foo1(x):
    ...     return x
    >>> pytest.warns(DeprecationWarning, foo1, 1)
    1
    >>> def newfun(x):
    ...     return 0
    >>> @deprecated(newfun, "1.1")
    ... def foo2(x):
    ...     return x
    >>> pytest.warns(DeprecationWarning, foo2, 1)
    0
    >>>
    """

    def outer(oldfun):
        def inner(*args, **kwargs):
            msg = f"{oldfun.__name__} is deprecated"
            if version is not None:
                msg += f"will be removed in version {version};"
            if replacement is not None:
                msg += f"; use {replacement} instead"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            if callable(replacement):
                return replacement(*args, **kwargs)
            return oldfun(*args, **kwargs)

        return inner

    return outer


def refetch(model_instance):
    """Reload model instance from the database."""
    return model_instance.__class__.objects.get(pk=model_instance.pk)


def get_classname(o):
    """Return the classname of an object r a class.

    :param o:
    :return:
    """
    target = o if inspect.isclass(o) or callable(o) else o.__class__
    try:
        return target.__qualname__
    except AttributeError:  # pragma: no cover
        return target.__name__


def fqn(o):
    """Return the fully qualified class name of an object or a class.

    :param o: object or class
    :return: class name

    >>> import concurrency.fields
    >>> fqn("str")
    Traceback (most recent call last):
    ...
    ValueError: Invalid argument `str`
    >>> class A:
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

    if hasattr(o, "__module__"):
        parts.extend((o.__module__, get_classname(o)))
    elif inspect.ismodule(o):
        return o.__name__
    if not parts:
        msg = f"Invalid argument `{o}`"
        raise ValueError(msg)
    return ".".join(parts)


def flatten(iterable):
    """Flat sequence into list.

    flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    :param sequence: any object that implements iterable protocol (see: :ref:`typeiter`)
    :return: list

    Examples:
    >>> from adminactions.utils import flatten
    >>> [1, 2, [3, 4], (5, 6)]
    [1, 2, [3, 4], (5, 6)]

    >>> flatten([[[1, 2, 3], (42, None)], [4, 5], [6], 7, (8, 9, 10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]

    """
    result = []
    for el in iterable:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return list(result)
