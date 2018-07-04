AutoMockMixin
=============

It's been my experience that when you're writing a TestCase that tests a specific function and that
function needs to mock one (or more) of the functions that it uses, that function needs to be mocked
throughout the entirety of the TestCase. The :any:`AutoMockMixin` helps alleviate the burden this
can cause.

:any:`mock.patch` is typically used for most cases as a decorator on the test function like this::

    # tests/test_foo.py
    from unittest import mock

    from tests import BaseTestCase
    
    from myproject import foo


    class TestFoo(BaseTestCase):
        @mock.patch('myproject.bar')
        def test_foo(self, mocked_bar):
            mocked_bar.return_value = 'baz'
            self.assertTrue(foo())

This works nicely when their is only a single function to mock and is even better if only one test needs
to mock. However, if every test needs to mock and if each test needs more than one function to mock
writing all of those ``mock.patch`` decorators can become hairy::

    # tests/test_foo.py
    
    class TestFoo(BaseTestCase):
        @mock.patch('myproject.bar')
        @mock.patch('myproject.baz')
        @mock.patch('myproject.biz')
        @mock.patch('myproject.boom')
        def test_1(self, bar, baz, biz, boom):
            # ...

        @mock.patch('myproject.bar')
        @mock.patch('myproject.baz')
        @mock.patch('myproject.biz')
        @mock.patch('myproject.boom')
        def test_2(self, bar, baz, biz, boom):
            # ...
        
        # ...

It's for times like this that you can return value of ``mock.patch`` to set up mocking in ``setUp()`` and
``tearDown()``::

    # tests/test_foo.py

    class TestFoo(BaseTestCase):
        def setUp(self):
            super(TestFoo, self).setUp()
            self.bar_patcher = mock.patch('myproject.bar')
            self.bar = self.bar_patcher.start()
            
            self.baz_patcher = mock.patch('myproject.baz')
            self.baz = self.bar_patcher.start()
            
            self.biz_patcher = mock.patch('myproject.biz')
            self.biz = self.bar_patcher.start()
        
        def tearDown(self):
            super(TestFoo, self).tearDown()
            self.bar_patcher.stop()
            self.bar_patcher = None
            self.bar = None
            
            self.baz_patcher.stop()
            self.baz_patcher = None
            self.baz = None
            
            self.biz_patcher.stop()
            self.biz_patcher = None
            self.biz = None

        def test_1(self):
            self.bar.return_value = 'baz'
            self.baz.return_value = True
            self.biz.return_value = 'asdf'
            self.AssertTrue(foo())

This kind of a setup only requires you to declare the mocked function once, but even this is fairly
tedious. This is where the :any:`AutoMockMixin` comes in handy. Using it, the above to examples can be rewritten
as::

    # tests/test_foo.py
    from granite.testcase import AutoMockMixin

    from tests import BaseTestCase

    class TestFoo(AutoMockMixin, BaseTestCase):
        bar = mock.patch('myproject.bar')
        baz = mock.patch('myproject.baz')
        biz = mock.patch('myproject.biz')
        boom = mock.patch('myproject.boom')

        def test_1(self):
            self.bar.return_value = 'baz'
            self.baz.return_value = True
            self.biz.return_value = 'asdf'
            self.AssertTrue(foo())

Ahhh, much nicer. We no longer have to worry about managing the state of mock patching setup and teardown
as the mixin does all of that work for us!

.. Note:: The ``AutoMockMixin`` not only works with ``mock.patch``, but it also works with ``mock.dict``
          and ``mock.object``.
