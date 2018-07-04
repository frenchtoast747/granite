"""
Provides utilities for setting a proper environment for testing.
"""
import collections
import fnmatch
import functools
import hashlib
import os
import shutil
import tempfile
import textwrap

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from granite.utils import cached_property, path_as_key


CHUNK_SIZE_MB = 15 * 1024 * 1024  # 15MB


class TemplateNotFoundError(Exception):
    """
    Raised when a template name was requested but not found in the available
    directories
    """


class Renderable(object):
    """
    An interface for objects that can be rendered.
    """
    template = None
    """
    The name of the template that instances of this class should use when rendering.
    This attribute is required and must be set by subclasses.
    """
    template_dirs = None
    """
    The template search path; a list of strings. When searching for a template
    by name, then the first file found on the path will be chosen. This attribute
    is required and must be set by subclasses.
    """
    _environment = None

    def get_environment(self, template_directories):
        """
        Gets the jinja2.Environment instance needed for loading the templates.

        Subclasses should override this if they need more customized power.

        Args:
            template_directories (list): a list of directories to search
                                         through

        Returns:

        """
        if self._environment is None:
            self._environment = Environment(
                loader=FileSystemLoader(template_directories),
                trim_blocks=True,
                undefined=StrictUndefined
            )
        return self._environment

    def get_template(self):
        """
        Gets the template used by this class for rendering.

        Subclasses can override this method is updating the `template` and
        ``template_dirs`` attributes is not sufficient.

        Returns:
            jinja2.Template: the template used to render
        """
        if self.template is None:
            raise AttributeError(
                'The class "{}" needs to define the "template" attribute '
                'which is a string of the name of the template used to '
                'render. Or, override the get_template() method in order to '
                'find the template that this class uses.'
                .format(self.__class__.__name__)
            )
        if self.template_dirs is None:
            raise AttributeError(
                'The class "{}" needs to define the "template_dirs" '
                'attribute which should be a list of directories to search '
                'through when looking for the template whose name is given '
                'by the "template" attribute. Or, override the '
                'get_template() method in order to find the template that '
                'this class uses.'
                .format(self.__class__.__name__)
            )

        template_name = self.template
        # yes, this is an iterable! if not, it's the users fault.
        for d in self.template_dirs:  # pylint: disable=not-an-iterable
            if os.path.exists(os.path.join(d, template_name)):
                break
        else:
            raise TemplateNotFoundError(
                'Cannot find template name "{}" in the following directories:'
                '\n{}'
                .format(template_name, '\n'.join(self.template_dirs))
            )

        env = self.get_environment(self.template_dirs)

        return env.get_template(template_name)

    def get_context(self):
        """
        Gets the context (or scope) used when rendering this class's template.

        By default, the context is set to all of the available attributes on
        this class. This means that if ``self.foo`` is set to ``'bar'``, then
        the variable ``{{ foo }}`` in the template will be rendered as the
        string ``bar``.

        Returns:
            dict: the context used for rendering. A mapping of variable name
                  to variable value as to be used in the template.
        """
        context = {}
        context.update(self.__class__.__dict__)
        context.update(self.__dict__)
        return context

    def render(self):
        """
        Renders the template as found by get_template() using the context as
        found by get_context() and returns the rendered string.

        Returns:
            str: the result of rendering the template with the context
        """
        context = self.get_context()
        template = self.get_template()
        result = template.render(context)

        return result


class RenderedFile(Renderable):
    """
    A file that will be rendered to disk.

    This class represents a file that, upon rendering, will appear on disk.
    By default, any attribute (instance or class) will appear in the context
    of the template. E.g., having an attribute of ``self.foo`` will make the
    ``foo`` variable exist within the template.

    This class provides a "content" variable and should serve as an area of the
    template that can be appended to on a per-test basis. Use the add_content()
    method in order to add more content to the template at the time of render.
    This allows for content to be added over a period of time either as
    subsequent calls in the same test, through the setUp, or setUp calls in
    multiple classes (via inheritance).

    Subclasses can override the get_context() method in order to alter the
    context (variable scope) provided to the template on render. See the
    get_context() method's documentation for more details.

    While this class can be used by itself (note that the instances attributes
    ``template`` and ``template_dirs`` must be set before rendering!) the
    intended use is to subclass this class and define class-level attributes
    for ``template`` and ``template_dirs``. This makes it so that a base class
    can point to a common template directory (through the template_dirs
    attribute) and all subclasses of it can supply the ``template`` attribute
    in order to determine which template to choose.

    Args:
        filename (str): the full path to where the file should exist on disk
                        when rendered

    Examples::

        # tests/environment.py
        # assume that the templates directory is:
        # tests/templates
        from granite.environment import RenderedFile
        from granite.testcase import TestCase, TempProjectMixin


        class MyRenderedFile(RenderedFile):
            template_dirs = [
                os.path.join(os.path.dirname(__file__), 'templates')]


        # assume that tests/templates/template.py exists
        # and looks something like this:
        print('Hello!')
        print(
            '''
             {{ content }}
            '''
        )
        print('This test is currently running: {{ id }}')

        class PythonScript(MyRenderedFile):
            template = 'template.py'


        class MyTestCase(TempProjectMixin, TestCase):
            def setUp(self):
                super(MyTestCase, self).setUp()
                self.script = PythonScript(
                    os.path.join(self.temp_project.path, 'my_file.py'))
                self.script.add_content('My name is Aaron')

            def test_the_thing(self):
                # setting the `id` attribute provides the `id`
                # context variable in the template
                self.script.id = self.id()
                self.script.render()
                with open(self.script.full_name) as f:
                    self.assertEqual(
                        f.read(),
                        \"\"\"
                        print('Hello!')
                        print(
                            '''
                            My name is Aaron
                            '''
                        )
                        print('This test is currently running: test_the_thing')
                        \"\"\"
                    )
    """
    DISABLE_ESCAPING = False
    """
    By default, the value in the "content" template variable is escaped. 
    This makes adding content for script/language files (via add_content()) 
    much easier to read and maintain as script/language files usually 
    interpret the special esacped characters differently. Set this attribute 
    to True in order to disable this functionality.
    """
    WRITE_MODE = 'w'
    """
    When rendering the file, defaults to non-binary mode. Set this to 'wb' 
    or something similar for different behavior when writing the rendered 
    contents to a file.
    """
    ADD_NEWLINE = True
    """
    Determines whether a newline should be added at the end of the file or 
    not. When generating C code to be compiled by the ARM/GCC compiler, 
    this makes the compiler happy. Defaults to True. Set to False to disable.
    """
    path = ''
    """
    The path to this rendered file (without the filename itself)
    """
    filename = ''
    """
    The name of the rendered file (without the path)
    """
    full_name = ''
    """
    the full path to the file
    """

    def __init__(self, filename=''):
        self.full_name = filename
        self.path, self.filename = os.path.split(filename)
        self.content = []

    def get_context(self):
        """
        Gets the context needed for rendering the file associated with this
        instance.

        A context is simply the template's scope of variables and functions.

        Returns:
            dict: the variable names and their values; the scope to appear in
                  the template
        """
        context = super(RenderedFile, self).get_context()
        content = '\n'.join(self.content)
        if not self.DISABLE_ESCAPING:
            content = content.replace('\\', r'\\')
        context['content'] = content
        return context

    def add_content(self, content):
        """
        Adds a string to the "content" variable available to the template.

        Args:
            content (str or List[str]): a single string or a list of strings to
                                        add to the content variable.
        """
        if isinstance(content, str):
            content = [content]
        self.content.extend(content)

    def render(self):
        """
        Renders the template and writes the contents to disk to this instance's
        filename.
        """
        contents = super(RenderedFile, self).render()
        filename = os.path.join(self.path, self.filename)
        with open(filename, self.WRITE_MODE) as f:
            f.write(contents + '\n' if self.ADD_NEWLINE else '')


class SimpleFile(RenderedFile):
    """
    Follows the renderable interface and allows for building up a file with
    ``add_content()`` then rendering and writing to disk at a later time.

    This class doesn't provide any sort of templating functionality. It just makes it
    easier to incorporate simple file writing into a framework that expects a Renderable.
    """

    def render(self):
        """
        Renders all of the contents to the filename given.
        """
        with open(os.path.join(self.path, self.filename), self.WRITE_MODE) as f:
            f.write('\n'.join(self.content) + '\n' if self.ADD_NEWLINE else '')


class TemporaryProject(object):
    """
    An interface for interacting with a temporary directory.

    A temp directory is created on instantiation and it is deleted
    (recursively) when this object is destroyed.

    Keyword Args:
        path (str): path of a directory to use for the temporary
                    directory if specified. If the directory already
                    exists, it is recursively deleted and then created.
                    Otherwise, if the directory doesn't exist, it (and
                    any intermediate directories) are created.
        preserve (bool): if set to ``True``, this directory will not
                         be destroyed. Useful for debugging tests.
    """
    TEMP_PREFIX = 'gprj_'
    """
    This is the prefix used for the new temp directory.
    """

    def __init__(self, path='', preserve=False):
        self.preserve = preserve

        if path:
            if os.path.exists(path):
                shutil.rmtree(path, onerror=_handle_error)
            # More often than not, the reason this fails is because
            # the user is currently in the same directory, at least
            # on Windows.
            if not os.path.exists(path):
                os.makedirs(path)

            self.path = path
        else:
            self.path = tempfile.mkdtemp(prefix=self.TEMP_PREFIX)

    def abspath(self, filename):
        """
        Get the absolute path to the filename found in the temp dir.

        Notes:

            * Always use forward slashes in paths.
            * This method does not check if the path is valid. If the
              filename given doesn't exist, an exception is not raised.

        Args:
            filename (str): the relative path to the file within this
                            temp directory

        Returns:
            str: the absolute path to the file within the temp directory.
        """
        return os.path.normpath(os.path.join(self.path, filename))

    def read(self, filename, mode='r'):
        """
        Read the contents of the file found in the temp directory.

        Args:
            filename (str): the path to the file in the temp dir.
            mode (str): a valid mode to open(). defaults to `'r'`

        Returns:
            The contents of the file.
        """
        filename = self.abspath(filename)

        with open(filename, mode=mode) as f:
            return f.read()

    def write(self, filename, contents='', mode='w', dedent=True):
        """
        Write the given contents to the file in the temp dir.

        If the file or the directories to the file do not exist,
        they will be created.

        If the file already exists, its contents will be overwritten
        with the new contents unless mode is set to some variant
        of append: (``a``, ``ab``).

        Specify the dedent flag to automatically call ``textwrap.dedent``
        on the contents before writing. This is especially useful when writing
        contents that depend on whitespace being exact (e.g. writing a
        Python script). This defaults to ``True`` except when the mode
        contains ``'b'``

        Args:
            filename (str): the relative path to a file in the temp dir
            contents (any): any data to write to the file
            mode (str): a valid open() mode
            dedent (bool): automatically dedent the contents
                           (default: ``True``)
        """
        path, filename = os.path.split(filename)
        path = self.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path)

        if dedent and 'b' not in mode:
            contents = textwrap.dedent(contents)

        with open(os.path.join(path, filename), 'w') as f:
            f.write(contents)

    def remove(self, filename):
        """
        Removes the filename found in the temp dir.

        Args:
            filename (str): the relative path to the file
        """
        os.remove(self.abspath(filename))

    def touch(self, filename, times=None):
        """
        Creates or updates timestamp on file given by filename.

        Args:
            filename (str): the filename to touch
            times (Tuple[int, int]): see os.utime for more information on this
            parameter.
        """
        filename = self.abspath(filename)
        with open(filename):
            os.utime(filename, times)

    def glob(self, pattern, start='', absolute=False):
        """
        Recursively searches through the temp dir for a filename that
        matches the given pattern and returns the first one that matches.

        Args:
            pattern (str): the glob pattern to match the filenames against.
                           Uses the fnmatch module's fnmatch() function to
                           determine matches.
            start (str): a directory relative to the root of the temp dir
                         to start searching from.
            absolute (bool): whether the returned path should be an absolute
                             path; defaults to being relative to the temp
                             project.

        Returns:
            str: the relative path to the first filename that matches pattern
                 unless the absolute flag is given. If a match is not found
                 None is returned.
        """
        for root, _, filenames in os.walk(os.path.join(self.path, start)):
            for f in filenames:
                path = os.path.relpath(os.path.join(root, f), start=self.path)
                if fnmatch.fnmatch(path, pattern):
                    if absolute:
                        return os.path.join(self.path, path)
                    return path

        return None

    def snapshot(self):
        """
        Creates a snapshot of the current state of this temp dir.

        Returns:
            Snapshot: the snapshot.
        """
        return Snapshot(self.path)

    def copy_project(self, dest, overwrite=False, symlinks=False, ignore=None):
        """
        Allows for a copying the temp project to the destination given.

        This provides test authors with the ability to preserve a tes
        environment at any point during a test.

        By default, if the given destination is a directory that already
        exists, an error will be raised (shutil.copytree's error). Set the
        ``overwrite`` flag to ``True`` to overwrite an existing directory by
        first removing it and then copying the temp project.

        Args:
            dest (str): the destination directory
            overwrite (bool): if the directory exists, this will remove it
                              first before copying
            symlinks (bool): passed to shutil.copytree: should symlinks
                             be traversed?
            ignore (bool): ignore errors during copy?
        """
        if overwrite and os.path.exists(dest):
            if os.path.dirname(dest) == dest:
                raise Exception(
                    'It appears you have specified the root of the file '
                    'system as the destination to copy to. Will not copy '
                    'temp directory to dest: {}'.format(dest)
                )
            shutil.rmtree(dest)
        shutil.copytree(self.path, dest, symlinks=symlinks, ignore=ignore)

    def teardown(self):
        """
        Provides a public way to delete the directory that this temp project
        manages.

        This allows for the temporary directory to be cleaned up on demand.

        Ignores all errors.
        """
        if not self.preserve and os.path.exists(self.path):
            shutil.rmtree(self.path, ignore_errors=True)

    def __del__(self):
        self.teardown()


FileStat = collections.namedtuple(
    'FileStat', [
        'st_mode',
        'st_ino',
        'st_dev',
        'st_nlink',
        'st_uid',
        'st_gid',
        'st_size',
        'st_atime',
        'st_mtime',
        'st_ctime',
        'md5',
    ]
)
"""
Mimics the os.stat() stat result object except this also includes the md5 hash
of the file.
"""


class Snapshot(object):
    """
    A snapshot of the state of the given directory at the time called.

    This will recursively traverse the given directory and note all of the
    files and directories within it. For the most part, a snapshot is useless
    by itself and is more useful when another snapshot is created and compared
    with the first.

    For example::

        some_dir = 'path/to/some/dir'
        s1 = Snapshot(some_dir)
        with open(os.path.join(some_dir, 'hello.txt'), 'w') as f:
            f.write('Hello, World!')
        s2 = Snapshot(some_dir)

        diff = s2 - s1

        assert diff.added == ['hello.txt']

    To see the difference between two snapshots, simply subtract one snapshot
    from the other. This creates a SnapshotDiff object with the attributes
    ``added``, ``removed``, ``modified``, and ``touched``. See the
    :class:`SnapshotDiff` documentation for more information.

    Note: this does not keep track of directory information, only files.
    Also Note: the paths stored in both the snapshot and in the diff are
    relative to the root of the snapshot directory.

    Args:
        directory (str): the directory to take a snapshot of
    """

    class SnapshotDiff(object):
        """
        The difference between Snapshot ``a`` and Snapshot
        ``b```.

        A difference object will have four attributes.
        """
        def __init__(self, a, b):
            # a "diff" is "a - b"
            self.a = a
            self.b = b

        @cached_property
        def added(self):
            """
            a collection of files that are new in ``a``, but not in ``b``
            """
            result = set()
            for path in self.a:
                if path not in self.b:
                    result.add(path)

            return result

        @cached_property
        def removed(self):
            """
            a collection of files that are in ``b``, but no longer in ``a``
            """
            result = set()
            for path in self.b:
                if path not in self.a:
                    result.add(path)

            return result

        @cached_property
        def modified(self):
            """
            a collection of files whose contents have changed between ``a``
            and ``b``
            """
            result = set()
            for path in self.a:
                if path in self.b:
                    if self.a[path].md5 != self.b[path].md5:
                        result.add(path)

            return result

        @cached_property
        def touched(self):
            """
            a collection of files whose timestamps have changed between ``a``
            and ``b``, but their contents have not changed.
            """
            result = set()
            for path in self.a:
                if path in self.b:
                    a = self.a[path]
                    b = self.b[path]
                    # if the modified time is not the same,
                    # but the contents are
                    if a.st_mtime != b.st_mtime and a.md5 == b.md5:
                        result.add(path)

            return result

    def __init__(self, directory):
        self.root = directory
        self.paths = {}

        for root, _, files in os.walk(directory):
            for path in files:
                path = os.path.join(root, path)
                stat = self._create_stat(os.stat(path), self._hash_file(path))
                self.paths[path_as_key(path, relative_to=directory)] = stat

    def _create_stat(self, stat_result, md5):
        kwargs = {}
        for field in FileStat._fields:
            # the only field that will me None will be "md5".
            # we'll set that later.
            value = getattr(stat_result, field, None)
            kwargs[field] = value
        kwargs['md5'] = md5

        return FileStat(**kwargs)

    def _hash_file(self, filename):
        h = hashlib.md5()
        with open(filename, 'rb') as f:
            for chunk in iter(functools.partial(f.read, CHUNK_SIZE_MB), b''):
                h.update(chunk)

        return h.hexdigest()

    def _massage_path(self, path):
        """
        Performs simple type validation on the given path and then converts
        it to its unique key form.
        """
        if not isinstance(path, str):
            raise ValueError(
                'The value given is not a path: "{}:{}"'
                .format(type(path), path)
            )

        if not os.path.isabs(path):
            path = os.path.join(self.root, path)

        path = path_as_key(path, relative_to=self.root)

        return path

    def __contains__(self, path):
        """
        Checks to see if the given path is found in this snapshot.

        Returns:
            bool: is path inside of this snapshot?
        """
        path = self._massage_path(path)

        return path in self.paths

    def __getitem__(self, path):
        """
        Gets the metadata stored for the given file

        Args:
            path (str): a path that should exist relative to the snapshot's
                        directory

        Returns:
            FileStat: a namedtuple containing os.stat information of the
                        filename.
        """
        path = self._massage_path(path)

        return self.paths[path]

    def __iter__(self):
        """
        Returns:
            iter: an iterator over all of the files underneath this snapshot's directory.
        """
        return iter(self.paths)

    def __sub__(self, other):
        """
        Creates a SnapshotDiff between this snapshot and the other snapshot.

        See the documentation on the SnapshotDiff for more information.
        """
        if not isinstance(other, Snapshot):
            raise TypeError(
                'Cannot create diff with object of type "{}"'
                .format(type(other))
            )
        return self.SnapshotDiff(self, other)


def _handle_error(_, path, excinfo):  # pragma: no cover
    """
    Implements the shutil.rmtree onerror interface.

    This checks to see if the item to be deleted that raised an error
    is a directory. If it is, just ignore it. More often than not, the
    presence of a directory is not enough to cause failures.
    """
    if not (os.path.exists(path) or os.path.isdir(path)):
        _, exception, _ = excinfo
        raise exception

