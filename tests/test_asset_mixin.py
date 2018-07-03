import os
import re

from tests import BaseTestCase

from granite.testcase import AssetMixin, AssetNotFound


THIS_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(THIS_DIR, 'assets')


class TestAssetMixin(AssetMixin, BaseTestCase):
    ASSET_DIR = ASSET_DIR

    def assert_asset_filename_is_correct(self, *parts):
        filename = self.get_asset_filename(*parts)
        self.assertEqual(filename, os.path.join(ASSET_DIR, *parts))

    def test_that_an_asset_filename_can_be_retrieved(self):
        self.assert_asset_filename_is_correct('some_asset_file.txt')

    def test_that_a_nested_filename_can_be_retrieved(self):
        self.assert_asset_filename_is_correct('some_directory/nested_asset_file.txt')

    def test_that_an_invalid_asset_filename_raises(self):
        parts = ('invalid', 'parts')
        # the repr of a tuple contains parens which we want to escape
        # so that they're not interpreted as regex groupings.
        repr_parts = re.escape(repr(parts))
        self.assertRaisesRegexp(
            AssetNotFound, '"{}"'.format(repr_parts),
            self.get_asset_filename, 'invalid', 'parts'
        )

    def test_that_a_files_contents_are_returned(self):
        actual = self.read_asset_file('some_asset_file.txt').strip()
        expected = 'Hi. I am an asset file. :)'

        self.assertEqual(actual, expected)

    def test_that_a_nested_asset_files_contents_are_returned(self):
        actual = self.read_asset_file('some_directory/nested_asset_file.txt').strip()
        expected = 'Hi. I am a nested asset file. :)'

        self.assertEqual(actual, expected)

    def test_that_an_invalid_filename_to_be_read_raises(self):
        parts = ('invalid', 'parts')
        # the repr of a tuple contains parens which we want to escape
        # so that they're not interpreted as regex groupings.
        repr_parts = re.escape(repr(parts))
        self.assertRaisesRegexp(
            AssetNotFound, '"{}"'.format(repr_parts),
            self.read_asset_file, 'invalid', 'parts'
        )
