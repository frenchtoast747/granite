A Simple Example of Using Granite
=================================

Installation
------------

To install Granite, issue the following pip command in your favorite shell::

    pip install granite


Toy Project
-----------

Let's assume that we're working on the following toy project::

    dev
    +---src
    |   \---example
    |           foo.py
    |           __init__.py
    |
    \---tests
            __init__.py

We have a Python package named ``example`` which contains a module named ``foo``. Inside
of the ``foo`` module, is the ``bar`` function::

    # example/foo.py

    def bar():
        """
        Returns:
            str: 'baz'
        """
        return 'baz'

To make sure that our Python package is functioning properly, we need to write a test for
it. To do that, we will need to create a test module that tests the ``bar()`` function.
Before we can do that that, we need to set up Granite to work with our testing structure.

Setting up Granite
------------------

Inside of ``tests/__init__.py`` import granite's :any:`TestCase` class and then
create a base test case class that inherits from it::

    # tests/__init__.py
    from granite.testcase import TestCase


    class BaseTestCase(TestCase):
        """
        This is the base test case class. All other test cases should inherit from this one.
        """

This provides a common place for helper methods, configuration, etc. for all tests that we
might need to write for our project. If for some reason we need to make a change that can
affect all tests, since all tests should, in some way, inherit from this base class, all
tests will get the new change by simply updating this base class.

It is at this point, that you can also add any of the other available mixins supplied by
the :any:`granite.testcase` module and add them to the list of base classes. The Granite
:any:`TestCase` class comes with a few additional assert methods. Each of these assert methods
start with ``assert_`` instead of ``unittest.TestCase``'s scheme of ``assertCamelCase``. Check
out the :any:`TestCase` documentation for specifics.


Testing The foo Module
----------------------

In order to test the foo module, we need to create a new module named ``test_foo.py`` in the
``tests/`` directory. Note that ``tests`` itself is a Python package since it contains an
``__init__.py``. This will allow us to import the ``BaseTestCase`` class set up in the above
step. Inside of ``test_foo.py`` place the following contents::

    # tests/test_foo.py
    from tests import BaseTestCase

    from example import foo


    class TestFoo(BaseTestCase):
        def test_that_bar_returns_baz(self):
            actual = foo.bar()
            expected = 'baz'
            self.assertEqual(actual, expected)


This creates the test case class ``TestFoo`` with a single test method
``test_that_bar_returns_baz``. ``foo.bar()`` is called and its return value is compared
with the expected return value.

That's it! A simple test for a simple function


A Slightly More Complicated Example
-----------------------------------

Yes. The above example was really simple and hardly uses Granite at all. In this example,
we're going to be using one of Granite's Mixin classes to add functionality to our tests.
The ``example`` project has expanded and added a new function in the ``foo`` module named
``count()``. The ``count()`` function takes in a filename, opens the file, counts the
occurrence of each character in the file, and returns a map of the character to the count::

    # example/foo.py
    from collections import Counter

    def count(filename):
        with open(filename) as f:
            return Counter(f.read())

In order to test this function, we will need a file on disk. Granite provides a Mixin
class called :any:`AssetMixin` that can be mixed in to a TestCase class in order to provide
asset file management.

First, let's create the asset file for this test. We'll do this by creating an ``assets``
directory. This can be placed anywhere in the project, but it's a good practice to keep the
asset files with the tests, so we'll put it underneath the ``tests`` directory. Inside of that asset
directory, we'll create an input file named ``count_input.txt`` that contains input for the
``count()`` function to read::

    \---tests
        \--- assets
                count_input.txt
            __init__.py
            test_foo.py

And ``count_input.txt`` contains the following::

    Hello, World


Next, we need to add the AssetMixin to one of our test case classes. Mixin classes can
be added at the global level (in the ``BaseTestCase`` class) or on a per-TestCase basis.
Right now, the ``count()`` function is the only function that needs asset file management,
so we will add the AssetMixin to the ``TestFoo`` test case class::

    # tests/test_foo.py
    import os

    from tests import BaseTestCase

    from granite.testcase import AssetMixin

    from example import foo


    class TestFoo(AssetMixin, BaseTestCase):
        ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
        # ...

We imported :any:`AssetMixin` from the :any:`granite.testcase` module and then added it to
the tuple of base classes on ``TestFoo``. Note that ``AssetMixin`` comes *before* the
``BaseTestCase`` class. This ensures that the Mixin class properly overrides the base class.
Then, we defined the class-level attribute ``ASSETS_DIR``. This attribute is required to be
defined by the ``AssetMixin`` and informs it the location of the ``assets/`` directory.

Now, let's add the test function::

    # tests/test_foo.py

    class TestFoo(AssetMixin, BaseTestCase):
        def test_that_count_returns_expected_mapping(self):
            filename = self.asset_filename('count_input.txt')

            actual = foo.count(filename)
            expected = {
                'l': 3, 'o': 2, ' ': 1, 'e': 1, 'd': 1, 'H': 1, ',': 1, 'r': 1, 'W': 1
            }

            self.assertEqual(actual, expected)

We used one of the helper methods provided by the ``AssetMixin`` in this test:
:any:`AssetMixin.get_asset_filename`. This particular function takes in a filename relative to
the asset directory given by ``ASSETS_DIR`` and returns the full path to that file. We can
then pass this filename to the ``count()`` function which reads it and performs its task.

There are other Mixins available in the :any:`granite.testcase` module and all are similar
in that they may or may not require class-level configuration attributes to be set and
all Mixin classes should come before the base TestCase class.


When Testing Requires A Temporary Directory
-------------------------------------------
Granite also provides a :any:`TemporaryProjectMixin` which will create a temporary directory
on test setUp and delete it and all of its contents on teardown. In addition to the temporary
directory management, the :any:`TemporaryProjectMixin` and its underlying :any:`TemporaryProject`
class provide accessor functions for interacting with that temporary directory.

First, declare your test case class with :any:`TemporaryProjectMixin` class::

    # tests/test_something.py

    class TestSomething(TemporaryProjectMixin, BaseTestCase):
        """..."""

That's all it takes to create and destroy temporary directories per test. Now, assume you have a function
named ``something()`` that takes in a directory and writes a file to it. The :any:`TemporaryProjectMixin`
adds an attribute named ``temp_project`` to the test instance. That attribute is an instance of :any:`TemporaryProject`.
We can access the temp project's temp directory by accessing ``self.temp_project.path``.
We can then test the ``something`` function like this::

    # tests/test_something.py

    class TestSomething(TemporaryProjectMixin, BaseTestCase):
        def test_something_writes_to_file(self):
            something(self.temp_project.path)
            self.assert_in_temp_file('Hello, World!', 'file_created_by_something.txt')

Note the use of the :any:`assert_in_temp_file` method. It is one of the methods provided by the
:any:`TemporaryProjectMixin`. Have a look at its other methods for more information.


Writing temp files to the Temporary Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :any:`TemporaryProject` instance stored in ``self.temp_project`` also provides various I/O methods
for file interaction. For example, the :any:`TemporaryProject.write` method will create a file named
``filename``, opened with ``mode``, and fill it with ``contents``::

    # tests/test_something_that_needs_a_file.py

    class TestSomethingThatNeedsAFile(TemporaryProjectMixin, BaseTestCase):
        def test_something_that_needs_a_file(self):
            self.temp_project.write('some/path/to/a/file.txt', 'Hello :)')
            output = something_that_needs_a_file(self.temp_project.abspath('some/path/to/a/file.txt')
            self.assertEqual(output, 'Hello :)')

Have a look at some of the other methods available for more information.


Taking a snapshot of the Temporary Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes it's necessary to know what changed within a temporary project. Use the :any:`snapshot` on
the ``self.temp_project`` in order to record a :any:`Snapshot` of the complete state of all files and directories
within the temp project. A snapshot by itself is somewhat useless, but with two snapshots, you can create
a diff of the state of the temp project. A :any:`SnapshotDiff` contains lists of ``added``, ``removed``,
``modified``, and ``touched`` files. Note that a ``touched`` file is one whose timestamp has changed,
but its contents have not. A ``modified`` file has had its contents change. For example::

    # tests/test_change_in_dir.py

    class TestChangeInDir(TemporaryProjectMixin, BaseTestCase):
        def test_that_dir_changed(self):
            start = self.temp_project.snapshot()
            self.temp_project.write('hello.txt')
            end = self.temp_project.snapshot()
            diff = end - start
            self.assertIn('hello.txt', diff.added)


Automatically mocking attributes
--------------------------------
When you find yourself mocking a specific function over and over, it becomes very tedious to
apply the ``@mock.patch`` decorator to every single ``test_*`` function. This is where using the
patch ``start()`` and ``stop()`` methods can be handy::

    # tests/test_mocking.py

    class TestMocking(BaseTestCase):
        def setUp(self):
            super(TestMocking, self).setUp()
            self.fn_patcher = mock.patch('path.to.fn')
            # call .start() to get the mocked function instance
            self.fn = self.fn_patcher.start()

        def tearDown(self):
            super(TestMocking, self).tearDown()
            # be sure to stop mocking.
            self.fn_patcher.stop()
            # clear our references
            self.fn_patcher = None
            self.fn = None

        def test_thing(self):
            call_function_under_test()
            self.fn.assert_called_once_with(hello='world')

        def test_other_thing(self):
            call_function_under_test(thing=False)
            self.fn.assert_not_called()

        # ...

This sort of setup works well when the same function to be mocked is needed by many or all tests in a
test case. However, when you need more than one function to be mocked, this sort of setup can become
tedious itself. Introducing: the :any:`AutoMockMixin`. Add this mixin to your test case class and
it automatically handles all of the set up and tear down of mocking leaving you with the mocked
function as the attribute. For example, the above example would be rewritten as::

    # tests/test_mocking.py

    class TestMocking(AutoMockMixin, BaseTestCase):
        fn = mock.patch('path.to.fn')
        other_fn = mock.patch('path.to.other.fn')

        def test_thing(self):
            call_function_under_test()
            self.fn.assert_called_once_with(hello='world')
            self.other_fn.assert_not_called()

        def test_other_thing(self):
            call_function_under_test(thing=False)
            self.fn.assert_not_called()
            self.other_fn.assert_called_once()

        # ...

The :any:`AutoMockMixin` works not only with ``mock.patch``, but also ``mock.object`` and ``mock.dict``.
