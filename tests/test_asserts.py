import sys

from tests import BaseTestCase


class TestAssertLength(BaseTestCase):
    def test_assert_length_passes_with_correct_length(self):
        self.assert_length([1, 2, 3], 3)

    def test_assert_length_fails_with_incorrect_length(self):
        self.assertRaises(AssertionError, self.assert_length, [], 3)

    def test_assert_length_fails_with_custom_message_with_incorrect_length(self):
        message = 'oh noes!'
        self.assertRaisesRegexp(
            AssertionError, message, self.assert_length, [], 3, msg=message)


class TestAssertIterableOfType(BaseTestCase):
    def test_that_assert_all_isinstance_passes_when_an_object_is_equal_to_single_type(self):
        self.assert_iterable_of_type(['asdf'], str)

    def test_that_assert_all_isinstance_passes_when_an_object_is_in_tuple_of_types(self):
        self.assert_iterable_of_type(['asdf'], (str, None))

    def test_that_assert_all_isinstance_fails_when_one_item_is_not_correct(self):
        self.assertRaises(AssertionError, self.assert_iterable_of_type, ['asdf', 1], str)


class TestAssertExists(BaseTestCase):
    def test_that_existing_path_passes(self):
        self.assert_exists(sys.executable)

    def test_that_non_existent_path_asserts(self):
        self.assertRaises(
            AssertionError, self.assert_exists,
            'some paTh that will hopefully never ever in the history of ever ever exist'
        )
