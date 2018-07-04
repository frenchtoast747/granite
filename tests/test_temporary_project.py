import os
import tempfile

from tests import BaseTestCase
from tests.utils import safe_remove

from granite.environment import TemporaryProject
from granite.testcase import TemporaryProjectMixin


class TestTempProjectMixin(TemporaryProjectMixin, BaseTestCase):
    def test_that_temporary_directory_is_created(self):
        self.assert_temp_path_exists()

    def test_writing_a_single_file_to_the_root_of_the_temp_project(self):
        self.temp_project.write('filename.txt')
        self.assertTrue(os.path.join(self.temp_project.path, 'filename.txt'))

    def test_writing_a_single_file_relative_to_the_root_of_the_temp_project(self):
        self.temp_project.write('path/to/filename.txt')
        self.assertTrue(os.path.join(self.temp_project.path, 'path', 'to', 'filename.txt'))

    def test_that_upon_destruction_of_temp_project_instance_temp_directory_is_deleted(self):
        path = self.temp_project.path
        # self.temp_project should be the only reference to the TempProject
        # instances, so setting it to None should cause the instance to be
        # garbage collected, thus calling its __del__, which should also
        # delete the temp project directory.
        del self.temp_project
        self.assertFalse(os.path.exists(path))

    def test_that_files_contents_can_be_read(self):
        filename = 'some_file.txt'
        expected = 'some contents'
        self.temp_project.write(filename, expected)
        actual = self.temp_project.read(filename)

        self.assertEqual(actual, expected)

    def test_abspath(self):
        filename = 'something_that_could_not_ever_possible_match.wut'
        self.temp_project.write(filename)

        abs_filename = self.temp_project.abspath(filename)
        self.assert_temp_path_exists(filename)
        self.assertTrue(os.path.isabs(abs_filename))

    def test_copy_project(self):
        new_temp_dir = tempfile.mkdtemp()
        new_dir = os.path.join(new_temp_dir, 'blah')

        filename = 'my_file.mine'
        self.temp_project.write(filename, 'ohai there.')

        self.temp_project.copy_project(new_dir)

        self.assert_exists(os.path.join(new_dir, filename))

        safe_remove(new_temp_dir)

    def test_copy_project_overwrite(self):
        new_temp_dir = tempfile.mkdtemp()

        filename = 'my_file.mine'
        self.temp_project.write(filename, 'ohai there.')

        self.temp_project.copy_project(new_temp_dir, overwrite=True)

        self.assert_exists(os.path.join(new_temp_dir, filename))

        safe_remove(new_temp_dir)

    def test_assert_in_temp_file(self):
        filename = 'my_file.txt'
        contents = 'contents to search for'
        self.temp_project.write(filename, contents)
        self.assert_in_temp_file(contents, filename)

    def test_assert_not_in_temp_file(self):
        filename = 'my_file.txt'
        contents = 'contents to search for'
        self.temp_project.write(filename, contents)
        self.assert_not_in_temp_file('something that should never ever match', filename)

    def test_custom_temp_dir(self):
        custom_dir = self.temp_project.abspath('my_dir')
        t = TemporaryProject(path=custom_dir)
        self.assert_exists(custom_dir)

        # This is not necessarily a test, per se, but it should call the code to remove
        # the existing code which will gather coverage and thus pass the tox tests.
        t.teardown()
        # delete t here so that it doesn't affect the temp directory once t is reassigned
        # below.
        del t
        # manually create the dir to make sure that it is first removed
        os.makedirs(custom_dir)
        self.assert_temp_path_exists(custom_dir)
        t = TemporaryProject(path=custom_dir)
        # use t.path here so that the garbage collector doesn't think t is dead.
        self.assert_temp_path_exists(t.path)
        self.assertEqual(t.path, custom_dir)

    def assert_glob_filename(self, pattern):
        expected = os.path.normpath('path/to/my/file.txt')
        self.temp_project.write(expected)
        # should not ever match
        self.temp_project.write('path/to/my/somefile.txt')

        actual = self.temp_project.glob(pattern)
        self.assertEqual(actual, expected)

        actual = self.temp_project.glob(pattern, absolute=True)
        expected = os.path.join(self.temp_project.path, expected)
        self.assertEqual(actual, expected)

    def test_complete_glob_filename(self):
        self.assert_glob_filename('*file.txt')

    def test_parent_dir_glob_with_exact_filename(self):
        self.assert_glob_filename('*/file.txt')

    def test_partial_path_glob_filename(self):
        self.assert_glob_filename('path/*/file.txt')

    def test_non_matching_glob_filename_pattern_returns_none(self):
        # the temp project should be empty here
        actual = self.temp_project.glob('path/to/something/non-existent')
        self.assertIsNone(actual)


class TestPreserveProject(TemporaryProjectMixin, BaseTestCase):
    PRESERVE_DIR = None
    ENABLE_PRESERVE = True

    @classmethod
    def setUpClass(cls):
        cls.PRESERVE_DIR = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        safe_remove(cls.PRESERVE_DIR)
        cls.PRESERVE_DIR = None

    def test_that_directory_persists_after_temp_project_object_is_destroyed(self):
        # make sure that the project exists
        self.assert_temp_path_exists()
        # manually teardown the project, with persist set to True,
        # this should do nothing to the directory on disk
        self.temp_project.teardown()
        path = self.temp_project.path
        self.temp_project = None
        self.assert_exists(path)
