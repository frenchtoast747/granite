"""
Extends unittest.
"""
from __future__ import absolute_import

import os
import inspect

from unittest import TestCase as StandardTestCase
from unittest.util import strclass

from granite.exceptions import MisconfiguredError, GraniteException
from granite.environment import TemporaryProject
from granite.utils import get_mock_patcher_types


class AssetNotFound(GraniteException):
    """Raised when an asset file requested is not found."""


class AssetDirectoryNotSet(GraniteException):
    """Raised when the ASSETS_DIR attribute is not set."""


class TestCaseMixin(object):
    """Base TestCase Mixin class. All Mixins should inherit this class."""


class AssetMixin(TestCaseMixin):
    """
    Provides support for accessing assets needed by tests.
    """
    ASSET_DIR = None

    def __init__(self, *args, **kwargs):
        super(AssetMixin, self).__init__(*args, **kwargs)
        if self.ASSET_DIR is None:
            raise MisconfiguredError(
                'The ASSET_DIR attribute must be set on the TestCase '
                'class "{}"'.format(self.__class__.__name__)
            )

    def get_asset_filename(self, *parts):
        """
        Gets the absolute filename of the asset file given by ``filename``
        and ``*parts`` relative to the asset directory.

        Treat this input like that of ``os.path.join``.

        Assume the absolute path to the ``ASSETS_DIR`` is
        ``/path/to/assets/`` and the assets directory contains
        ``some_file.txt``, then::

            >>> self.get_asset_filename('some_file.txt')
            'path/to/assets/some_file.txt'

        Raises:
            AssetNotFound: when the filename to search for is not found on disk.

        Returns:
            str: the absolute path to the asset file.
        """
        filename = os.path.join(self.ASSET_DIR, *parts)
        if not os.path.exists(filename):
            raise AssetNotFound(
                'self.get_asset_filename() was called with "{}" which constructed the filename '
                '"{}" and was not found. Make sure that your path is correct and that '
                'ASSET_DIR on your current or inherited TestCase classes is set '
                'appropriately.'.format(parts, filename)
            )
        return filename

    def read_asset_file(self, filename, *parts, **kwargs):
        """
        Gets the contents of the given asset filename.

        Internally this calls ``get_asset_filename()``

        Pass the optional keyword argument ``mode`` in oder to set the file
        mode. For example use ``mode='rb'`` to read in bytes.

        Args:
            filename:
            *parts:
            **kwargs:

        Returns:
            The contents of the file using the given read ``mode``.

        Raises:
            AssetNotFound: when the filename to search for is not found on disk.
        """
        filename = self.get_asset_filename(filename, *parts)
        with open(filename, mode=kwargs.pop('mode', 'r')) as f:
            return f.read()


class TemporaryProjectMixin(TestCaseMixin):
    """
    Provides support for temporary project (directory) creation on a per-test basis.

    In order to use this mixin, the base TestCase class should inherit this mixin. This
    provides a new attribute named ``temp_project`` which is an instance of TempProject.

    See the :class:`~granite.environment.TempProject` class for all of its methods for
    how to manipulate the created temp project.

    Example::

        import os

        from granite.testcase import TestCase, TemporaryProjectMixin

        class TestSomeThing(TemporaryProjectMixin, TestCase):
            def test_some_thing(self):
                # a new temporary directory has already been created by this point.
                # let's create a new file and add some contents:
                self.temp_project.write('some_file', 'Ohai :)')
                # get the temp_project's path by its .path attribute.
                # This proves that the file was created and exists on disk:
                self.assertTrue(os.path.exists(
                    os.path.join(self.temp_project.path, 'some_file')))
                # read the contents of a file relative to the temp project's directory:
                contents = self.temp_project.read('some_file')
                self.assertEqual(contents, 'Ohai :)')
    """
    TMP_DIR = None
    """
    Allows for setting the temp directory. Defaults to ``None`` which will use 
    Python's :any:`tempfile.mkdtemp` to make the temp directory.
    """
    PRESERVE_DIR = None
    """
    Sets where the preserved path should be dumped too. This overrides the ``TMP_DIR`` when
    ``ENABLE_PRESERVE`` is set to True.
    """
    ENABLE_PRESERVE = False
    """
    A flag indicating whether the temp project should be preserved after the temp project
    object is destroyed. If True, the directory will still exist allowing a user to view
    the state of the directory after a test has run. This works in tandem with the
    ``PRESERVE_DIR`` class attribute.
    """
    TemporaryProjectClass = TemporaryProject
    """
    Set this attribute to a class that implements the interface of
    :class:`~granite.environment.TemporaryProject`.
    This allows for creating a custom temporary project manager. A typical use case would
    be to subclass :class:`~granite.environment.TempProject` and override specific
    functionality then specify that new class here.
    """

    def __init__(self, *args, **kwargs):
        super(TemporaryProjectMixin, self).__init__(*args, **kwargs)
        self.temp_project = None

    def setUp(self):
        """
        Sets up the temporary project on test startup.
        """
        super(TemporaryProjectMixin, self).setUp()
        tmp_dir = self.TMP_DIR
        if self.ENABLE_PRESERVE and self.PRESERVE_DIR:
            tmp_dir = os.path.join(
                self.PRESERVE_DIR, self.__class__.__name__, self._testMethodName)
        self.temp_project = self.TemporaryProjectClass(
            path=tmp_dir, preserve=self.ENABLE_PRESERVE)

    def tearDown(self):
        """
        Deletes the temp project.
        """
        super(TemporaryProjectMixin, self).tearDown()
        self.temp_project = None

    def assert_in_temp_file(self, substring, filename, msg='', mode='r', not_in=False):
        """
        Asserts that the given contents are found in the file in the temp project.

        Args:
            substring (str): the substring to look for in the file's contents
            filename (str): the name of the file relative to the temp project
            msg (str):      the message to output in the event of a failure.
            mode (str):     the mode to open the file with. defaults to 'r'
            not_in (bool):  asserts that the contents are not in the file
        """
        method = self.assertNotIn if not_in else self.assertIn
        contents = self.temp_project.read(filename, mode=mode)
        method(substring, contents, msg=msg)

    def assert_not_in_temp_file(self, substring, filename, msg='', mode='r'):
        """
        Asserts that the given contents are not found in the file in the temp project.

        Args:
            substring (str): the substring to look for in the file's contents
            filename (str):  the name of the file relative to the temp project
            msg (str):       the message to output in the event of a failure.
            mode (str):      the mode to open the file with. defaults to 'r'
        """
        self.assert_in_temp_file(substring, filename, msg=msg, mode=mode, not_in=True)

    def assert_temp_path_exists(self, path='.', msg=''):
        """
        Asserts that the path given exists relative to the root of the temp project.

        Args:
            path (str): the string of the path relative to the root of the temp directory.
            msg (str):  a custom string to show in the event that this assertion fails.
        """
        if not msg:
            msg = (
                'The given path "{}" was expected to exist, in the temp project "{}", but '
                'it does not.'.format(path, self.temp_project.path)
            )
        self.assert_exists(os.path.join(self.temp_project.path, path), msg=msg)


class AutoMockMixin(TestCaseMixin):
    """
    Helps prevent the boilerplate of having mock patcher and object setup
    and teardown logic for every function needing to be mocked.
    """
    def setUp(self):
        super(AutoMockMixin, self).setUp()
        self.__mock_members = inspect.getmembers(
            self.__class__, predicate=lambda m: isinstance(m, get_mock_patcher_types()))

        for name, patcher in self.__mock_members:
            mock_object = patcher.start()
            setattr(self, name, mock_object)
            self.addCleanup(patcher.stop)


class TestCase(StandardTestCase):
    """
    Extends the Standard Library's TestCase class.
    """

    def __str__(self):
        """
        Returns a copy/paste-able representation of the test name.

        By default, a unittest.TestCase class will print out something like:
            `test_my_feature (test_my_features_module.FeatureTestCase)`
        which can't just be copied and pasted onto the command line in one go. You
        have to copy the part in the parens first, then copy the test name itself.
        This is somewhat annoying as usually the output only matters when a test fails
        and when a test fails, it is usually desirable to reproduce the error locally.
        """
        return "%s.%s" % (strclass(self.__class__), self._testMethodName)

    def assert_iterable_of_type(self, iterable, types, msg=''):
        """
        Assert that all items in the given iterable are of the given type(s).

        Args:
            iterable (Iterable): the items to check
            types (Union[object, tuple]): valid type input for isinstance.
            msg (str): optional message if the assertion fails
        """
        for idx, item in enumerate(iterable):
            if not isinstance(item, types):
                raise AssertionError(
                    'Element at index "{}" is not of type(s) "{!r}". {}'
                    .format(idx, types, msg)
                )

    def assert_length(self, sized, length, msg=''):
        """
        Asserts that the `sized` object has `length` number of items.

        Args:
            sized (Sized): any object that implements the __len__() method.
            length (int): the number of items that `sized` should contain
            msg (Optional[str]): a message to display in the event that this assert fails.

        Example::

            from granite.testcase import TestCase

            class MyTestCase(TestCase):
                def test_that_contents_are_correct_length(self):
                    contents = [1, 2, 3]
                    self.assert_length(contents, 3, msg='Some how, the length is not 3???')
        """
        self.assertEqual(len(sized), length, msg=msg)

    def assert_exists(self, path, msg=''):
        """
        Asserts that the given path exists on disk.

        This function acts like os.path.join() in that it can accept multiple arguments
        all of which will be joined together before checking for existence.

        Args:
            path (str): the root path to check for
            msg (str):  the message to show if the assertion fails.
        """
        if not msg:
            msg = 'The path "{}" was expected to exist, but does not.'
        self.assertTrue(os.path.exists(path), msg=msg)
