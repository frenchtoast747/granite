from tests import BaseTestCase

from granite.testcase import TemporaryProjectMixin


class TestDirectorySnapshot(TemporaryProjectMixin, BaseTestCase):
    def test_diff_attributes(self):
        self.temp_project.write('removed.txt', 'hello world')
        self.temp_project.write('touched.txt')
        self.temp_project.write('modified.txt')

        s1 = self.temp_project.snapshot()

        self.temp_project.write('added.txt')
        self.temp_project.remove('removed.txt')
        self.temp_project.touch('touched.txt')
        self.temp_project.write('modified.txt', 'la la la')

        s2 = self.temp_project.snapshot()

        d = s2 - s1

        self.assertIn('added.txt', d.added)
        self.assertIn('removed.txt', d.removed)
        self.assertIn('modified.txt', d.modified)
        self.assertIn('touched.txt', d.touched)

    def test_ds_minus_non_ds(self):
        s = self.temp_project.snapshot()
        with self.assertRaises(TypeError):
            s - 5

    def test_massage_path(self):
        s = self.temp_project.snapshot()
        self.assertRaises(ValueError, s._massage_path, 5)
