Asset Management
================

There are two times when tests need access to files on disk

* the function under test requires a file on disk (usually by filename)
* a function requires a large amount of data, specially formatted data, or
  the data is more easily stored as a file on disk rather than being embedded
  in the test itself. E.g.:

    * XML
    * JSON
    * Images
    * INI/Configuration files
    * A Python script
    * etc.

Granite supplies the :any:`AssetMixin` to provide support for easily accessing test asset files.

.. Note:: If you need to also write files to disk, check out :doc:`temporary_projects`.

Setup
-----

To setup, add the ``AssetMixin`` to the list of base classes on your TestCase class and create a
class level attribute ``ASSET_DIR`` that points to the directory containing your asset files::

    # tests/some_test.py
    import os

    from granite.testcase import TestCase, AssetMixin

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    class MyTestCase(AssetMixin, TestCase):
        # assume that the asset directory exists at `tests/assets`
        ASSET_DIR = os.path.join(THIS_DIR, 'assets')


.. Note:: The ``AssetMixin`` comes *before* the concrete ``TestCase`` class.

Getting Asset Filenames
-----------------------

Use :any:`get_asset_filename` to get the absolute path to a filename within the ``ASSET_DIR``.
For example::

    # tests/some_test.py

    def test_that_foo_can_read(self):
        # assume that `tests/assets/some_file.txt` exists
        filename = self.get_asset_filename('some_file.txt')
        # pass the absolute path to the foo() function
        foo(filename)

The path parameter acts just like ``os.path.join()`` and can accept multiple parameters to
be joined. For example::

    >>> self.get_asset_filename('path', 'to', 'my', 'file.txt')
    '/absolute/path/to/my/file.txt'

If the given path does not exist, an :any:`AssetNotFound` error will be raised::

    >>> self.get_asset_filename('path/to/some/nonexistent/file.txt')
    Traceback
        ...
    AssetNotFound: self.get_asset_filename() was called with ...

Reading from an Asset File
--------------------------

Use :any:`read_asset_file` to open the asset file and return its contents::

    # tests/some_test.py

    def test_that_xml_can_be_parsed(self):
        xml = self.read_asset_file('my.xml')
        root = foo(xml)
        self.assertEqual(etree.tostring(root), xml)

Under the hood, ``read_asset_file()`` uses ``get_asset_filename()`` so path also accepts multiple arguments
and will ``os.path.join()`` all of them together to form a single path.

Additionally, use the ``mode`` keyword argument to specify how the file should be opened. For example,
your function under test requires an image file that needs to be opened in binary mode::

    # tests/some_test.py

    def test_that_image_size_is_returned(self):
        img = self.read_asset_file('1920x1080.jpg', mode='rb')
        size = foo(img)
        self.assertEqual((1920, 1080), size)


Advanced setup
--------------
If you find that all (or most) of your tests require access to the asset directory, add the ``AssetMixin``
to your test's ``BaseTestCase`` class::

    # tests/__init__.py
    from granite.testcase import TestCase, AssetMixin

    class BaseTestCase(AssetMixin, TestCase):
        # assume that `tests/assets` exists
        ASSET_DIR = os.path.join(THIS_DIR, 'assets')

Then, simply inherit from your ``BaseTestCase`` in your child ``TestCase`` classes to get the asset
functionality::

    # tests/some_test.py
    from tests import BaseTestCase

    class TestSomething(BaseTestCase):
        # self.get_asset_filename() and self.read_asset_file() exist!


Using different directories per TestCase
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One test may require one directory, and another test may use another. Simply change the ``ASSET_DIR``
to use a different directory for the specific TestCase instance::

    # tests/some_test.py
    from tests import BaseTestCase

    class TestSomething(BaseTestCase):
        ASSET_DIR = os.path.join(THIS_DIR, 'other', 'assets')


Better asset organization
^^^^^^^^^^^^^^^^^^^^^^^^^

If your tests require a lot of asset files it's a good idea to try and organize files that are specific to
some tests into their own directory. For example, ``test_foo.py`` requires files ``a.txt`` and ``b.txt``
while ``test_bar.py`` requires ``c.txt`` and ``d.txt``. The resulting file structure is suggested::

    tests/
      \ assets
          \ foo
          | | - a.txt
          | | - b.txt
          \ bar
            | - c.txt
            | - d.txt

However, this requires every use of ``get_asset_filename()`` or ``read_asset_file()`` to require the
directory prefix (either ``foo`` or ``bar``). Instead, the ``BaseTestCase.ASSET_DIR`` attribute can
be extended::

    # tests/test_foo.py
    import os

    from tests import BaseTestCase

    class TestFoo(BaseTestCase):
        ASSET_DIR = os.path.join(BaseTestCase.ASSET_DIR, 'foo')

This way, if the asset directory is ever moved, the BaseTestCase class will be the only place that needs
to be updated.
