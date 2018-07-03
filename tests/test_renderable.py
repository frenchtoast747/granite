import os

from tests import BaseTestCase, TestCaseWithTempProject

from granite.environment import (
    File, Renderable, TemplateNotFoundError,
    SimpleFile
)


class MyRenderedFile(File):
    template_dirs = [os.path.join(os.path.dirname(__file__), 'templates')]
    template = 'test_renderable/template.txt'


class TestRenderable(BaseTestCase):
    def setUp(self):
        super(TestRenderable, self).setUp()
        self.r = Renderable()

    def test_template_attribute_is_none_raises(self):
        self.r.template_dirs = []
        self.assertRaisesRegexp(
            AttributeError, 'define the "template" attribute', self.r.get_template,)

    def test_template_dirs_attribute_is_none_raises(self):
        self.r.template = 'my_template'
        self.assertRaisesRegexp(
            AttributeError, 'define the "template_dirs" attribute', self.r.get_template)

    def test_template_not_found(self):
        self.r.template = 'Something that does not exist'
        self.r.template_dirs = ['some/place/that/does/not/exist']
        self.assertRaises(TemplateNotFoundError, self.r.get_template)


class TestRenderedFile(TestCaseWithTempProject):
    def setUp(self):
        super(TestRenderedFile, self).setUp()
        self.expected_filename = os.path.join(self.temp_project.path, 'my_file.txt')
        self.file = MyRenderedFile(self.expected_filename)
        self.file.foo = 'my foo value'

    def render_and_assert(self, substring):
        self.file.render()
        self.assert_in_file(substring)

    def assert_in_file(self, substring):
        with open(self.expected_filename) as f:
            self.assertIn(substring, f.read())

    def test_content(self):
        content = 'testing 123'
        self.file.add_content(content)

        self.render_and_assert('CONTENT: ' + content)

    def test_attribute_in_context(self):
        self.render_and_assert('FOO: ' + self.file.foo)


class TestSimpleFile(TestCaseWithTempProject):
    def test_that_file_is_written_and_contains_only_contents_provided(self):
        f = SimpleFile(os.path.join(self.temp_project.path, 'so_simple.txt'))
        f.add_content('Hello')
        f.add_content('World')
        f.render()

        with open(f.full_name) as fo:
            self.assertEqual('Hello\nWorld\n', fo.read())
