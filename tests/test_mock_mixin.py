try:
    from unittest import mock
except ImportError:
    import mock

from tests import BaseTestCase

from granite.testcase import AutoMockMixin


def fn_to_mock():
    return None

dict_to_mock = {'some_key': False}
expected_dict = {'new_key': 'new_value'}


class SomeClass(object):
    def some_method(self):
        return 'NOPE!'

some_instance = SomeClass()


class TestAutoMockMixin(AutoMockMixin, BaseTestCase):
    fn_to_mock = mock.patch(__name__ + '.fn_to_mock')
    mock_dict = mock.patch.dict(dict_to_mock, expected_dict, clear=True)
    some_method = mock.patch.object(some_instance, 'some_method')

    def test_that_class_attribute_becomes_a_patched_mock_object(self):
        expected = 'YAY!'
        self.fn_to_mock.return_value = expected
        self.assertEqual(fn_to_mock(), expected)

    def test_that_patch_dict_works(self):
        self.assertEqual(dict_to_mock, expected_dict)

    def test_that_patch_object_works(self):
        expected = 'hello?'
        self.some_method.return_value = expected
        self.assertEqual(some_instance.some_method(), expected)
