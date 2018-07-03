from granite.testcase import TestCase, TemporaryProjectMixin


class BaseTestCase(TestCase):
    """Base test case class that all tests should inherit from."""

    
    
class TestCaseWithTempProject(TemporaryProjectMixin, BaseTestCase):
    """Adds the temp project functionality as a concrete class."""