"""
Utility for internal library use.
"""
import os


def cached_property(fn):
    """
    Converts a class's method into property and cache's the getter value.

    Simple decorator a method with this function and it will be converted into a property
    (attribute access) and the calculation to retrieve the value will be cached so that
    the initial call performs the calculation, but subsequent calls will use the cache.
    """
    attr_name = '_' + fn.__name__

    def _wrapper(self):
        value = getattr(self, attr_name, None)
        if value is None:
            value = fn(self)
            setattr(self, attr_name, value)

        return value

    _wrapper.__name__ = fn.__name__
    _wrapper.__doc__ = fn.__doc__

    return property(_wrapper)


def path_as_key(path, relative_to=None):
    """
    Converts a path to a unique key.

    Paths can take on several unique forms but all describe the same node
    on the file system. This function will take a path and produce a key
    that is unique such that several paths that point to the same node
    on the file system will all be converted to the same path.

    This is useful for converting file paths to keys for a dictionary.

    Note: all paths will be separated by forward slashes.

    Args:
        path (str):        the path to convert.
        relative_to (str): make the key relative to this path

    Returns:
        str: the unique key from the path

    Examples::

        >>> path_as_key('./file.txt') == path_as_key('file.txt')
        True
    """
    # if it's not already absolute, make it so.
    path = os.path.abspath(path)
    # convert it relative to the CWD
    path = os.path.relpath(path, start=relative_to)
    # normalize it by removing all instances of "." and ".."
    path = os.path.normpath(path)
    # convert all backslashes to forward to normalized the path separators
    path = path.replace('\\', '/')
    return path


def _dummy_function():
    """Used by the get_mock_patcher_types() function"""


_dummy_dict = {}


def get_mock_patcher_types():
    """
    Gets the Classes of the mock.patcher functions.

    We're using this for the automatic mocking mixin in order
    to determine if a class-level attribute is a patcher instance.

    Returns:
        tuple: a unique list of the patcher types used by mock.
    """
    if get_mock_patcher_types.types is not None:
        return get_mock_patcher_types.types

    try:
        from unittest import mock
    except ImportError:
        import mock

    types = tuple({
        type(mock.patch(__name__ + '._dummy_function')),
        type(mock.patch.object(_dummy_function, 'some_method')),
        type(mock.patch.dict(_dummy_dict)),
    })

    get_mock_patcher_types.types = types

    return types


get_mock_patcher_types.types = None
