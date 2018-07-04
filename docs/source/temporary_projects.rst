Temporary Projects
==================

When you need to be able to create a small environment to read files from or to write files to,
you need to create a Temporary Project that only lasts as long as the test needs it. The
:any:`TemporaryProjectMixin` does just this.


Basic Setup
-----------

To setup, add the ``TemporaryProjectMixin`` to the list of base classes on your TestCase class::

    # test/test_foo.py
    from granite.testcase import TestCase, TemporaryProjectMixin

    class TestFoo(TemporaryProjectMixin, TestCase):
        # ...

On test ``setUp()``, the ``TemporaryProjectMixin`` will create a temporary directory and on
test ``tearDown()`` that temporary directory will be destroyed.

Interacting with the Temporary Project
--------------------------------------

The ``TemporaryProjectMixin`` adds a new attribute to the TestCase instance: ``temp_project``. This
attribute is an instance of the :any:`TemporaryProject` class and provides accessor methods for
interacting with the temporary directory.

.. automethod:: granite.environment.TemporaryProject.abspath
    :noindex:
.. automethod:: granite.environment.TemporaryProject.read
    :noindex:
.. automethod:: granite.environment.TemporaryProject.write
    :noindex:
.. automethod:: granite.environment.TemporaryProject.remove
    :noindex:
.. automethod:: granite.environment.TemporaryProject.touch
    :noindex:
.. automethod:: granite.environment.TemporaryProject.glob
    :noindex:
.. automethod:: granite.environment.TemporaryProject.snapshot
    :noindex:
.. automethod:: granite.environment.TemporaryProject.copy_project
    :noindex:
.. automethod:: granite.environment.TemporaryProject.teardown
    :noindex:

.. Note:: The ``temp_project`` attribute has a public ``.path`` attribute which holds the absolute
          path to the temporary directory.


Example of writing a file
^^^^^^^^^^^^^^^^^^^^^^^^^

When a file needs to be written to disk (a templated file, etc.) use the :any:`write` method of
the ``TemporaryProject`` to write that file to the temporary project::

    # tests/test_foo.py

    def test_that_file_is_written(self):
        # note that the path to the file should use forward
        # slashes (even on Windows!). The directories will be
        # created automatically.
        self.temp_project.write('path/to/some_file.txt', 'contents to write')

        # assert that the new file exists.
        # note: this uses the .path attribute of the `temp_project` in order
        #       to get the absolute path to the temporary directory
        self.assertTrue(
            os.path.exist(
                os.path.join(self.temp_project.path, 'path', 'to', 'some_file.txt')))

        # we can also assert that the new file exists by using the
        # TemporaryProjectMixin.assert_temp_path_exists() assert method.
        self.assert_temp_path_exists('path/to/some_file.txt')


TemporaryProjectMixin Assert Methods
------------------------------------

The ``TemporaryProjectMixin`` provides additional assert methods useful for asserting conditions on the
temporary project.

.. automethod:: granite.testcase.TemporaryProjectMixin.assert_in_temp_file
    :noindex:
.. automethod:: granite.testcase.TemporaryProjectMixin.assert_not_in_temp_file
    :noindex:
.. automethod:: granite.testcase.TemporaryProjectMixin.assert_temp_path_exists
    :noindex:

Taking A Snapshot of the Temporary Project
------------------------------------------

Sometimes it's necessary to know what changed within a temporary project. Use the :any:`snapshot` method on
the ``self.temp_project`` in order to record a :any:`Snapshot` of the complete state of all files and directories
within the temp project. A snapshot by itself is somewhat useless, but with two snapshots, you can create
a diff of the state of the temp project. A :any:`SnapshotDiff` contains lists of ``added``, ``removed``,
``modified``, and ``touched`` files. Note that a ``touched`` file is one whose timestamp has changed,
but its contents have not. A ``modified`` file has had its contents change.

Example::

    # tests/test_change_in_dir.py

    class TestChangeInDir(TemporaryProjectMixin, BaseTestCase):
        def test_that_dir_changed(self):
            start = self.temp_project.snapshot()
            self.temp_project.write('hello.txt')
            end = self.temp_project.snapshot()
            diff = end - start
            self.assertIn('hello.txt', diff.added)


Advanced Setup
--------------

The ``TemporaryProjectMixin`` class allows for supplying some class-level attributes in order to
configured the TestCase class.

.. autoattribute:: granite.testcase.TemporaryProjectMixin.TMP_DIR
    :noindex:
.. autoattribute:: granite.testcase.TemporaryProjectMixin.PRESERVE_DIR
    :noindex:
.. autoattribute:: granite.testcase.TemporaryProjectMixin.ENABLE_PRESERVE
    :noindex:
.. autoattribute:: granite.testcase.TemporaryProjectMixin.TemporaryProjectClass
    :noindex:


Setting a custom temp directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes it's desirable to be in control of the temp directory. In order to change the location of
the temporary directory, set the ``TMP_DIR`` attribute at the class level::

    # tests/test_foo.py
    import os

    from granite.testcase import TestCase, TemporaryProjectMixin

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    class TestFoo(TemporaryProjectMixin, TestCase):
        # set to be a directory named '.tmp' at the root of the project
        TMP_DIR = os.path.join(THIS_DIR, '..', '.tmp')

.. Note:: There probably isn't a good reason to change this. Hard-coding a single path
          will make running tests in parallel impossible, so it's probably best to stick to the default.
          The only reason that a deterministic temporary path may be desirable is to inspect the contents
          of the temporary directory before, during, or after a test run in order to assert that tests are
          running as expected or to debug a test. For this case see below for setting a preserve path.


Setting a preserve path for temporary project debugging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

During testing with temporary projects, inevitably it becomes desirable to preserve the temporary
directory in order to debug its contents. The ``TemporaryProjectMixin`` provides an option for
enabling the preservation of the temp project and setting a known location in order to view that
temporary directory::

    # tests/test_foo.py
    import os

    from granite.testcase import TestCase, TemporaryProjectMixin

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    class TestFoo(TemporaryProjectMixin, TestCase):
        # set to be a directory named '.tmp' at the root of the project
        PRESERVE_DIR = os.path.join(THIS_DIR, '..', '.tmp')
        # without this, the TMP_DIR option will still be used
        ENABLE_PRESERVE = True

        def test_foo(self):
            # ...

Setting the ``PRESERVE_DIR`` sets the root of all preserved directories. All temporary projects will
be created underneath this directory using the TestCase's class name for the first directory and the
resultant temp project will be created under another directory named after the test method.

For example, when the above ``test_foo`` is run, a temporary project will be created at
``.tmp/TestFoo/test_foo`` (relative to the project root). This allows for inspection of the temp
project contents after the test has run at a pre-determined path.

Note that the ``ENABLE_PRESERVE`` attribute can be parameterized based on command line arguments. For
this reason, it's a good idea to provide a concrete ``TemporaryProjectTestCase`` class or to make some
base class inherit the ``TemporaryProjectMixin`` so that the logic of enabling or disabling the
preservation of temp projects is all in one place::

    # tests/__init__.py
    import sys

    from granite.testcase import TestCase, TemporaryProjectMixin

    # either make *all* tests use the TemporaryProjectMixin
    class BaseTestCase(TemporaryProjectMixin, TestCase):
        # enable or disable preserve based on a command line flag
        ENABLE_PRESERVE = '--preserve' in sys.argv
        # set to be a directory named '.tmp' at the root of the project
        PRESERVE_DIR = os.path.join(THIS_DIR, '..', '.tmp')


    # or provide a concrete temp project test case class only for
    # tests that require a temp project
    class TempProjectTestCase(TemporaryProjectMixin, TestCase):
        # enable or disable preserve based on a command line flag
        ENABLE_PRESERVE = '--preserve' in sys.argv
        # set to be a directory named '.tmp' at the root of the project
        PRESERVE_DIR = os.path.join(THIS_DIR, '..', '.tmp')


Doing the above provides the preservation configuration in one spot and all later tests can benefit
by inheriting.