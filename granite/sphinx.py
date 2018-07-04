"""
Provides the main DocBuilder class for easily interfacing with sphinx to build
the project's documentation.
"""

from __future__ import absolute_import

import argparse
import os
import sys
import shutil


from sphinx.cmd import build
from sphinx.ext import apidoc

from granite.exceptions import GraniteException


class RequiredAttributeException(GraniteException):
    """Raised when an attribute on the DocBuilder class has not been defined"""
    def __init__(self, attribute, class_, description):
        super(RequiredAttributeException, self).__init__(
            'The required attribute, "{}", has not been defined on the class '
            '"{}". The attribute should contain {}'
            .format(attribute, class_.__name__, description)
        )


class DocBuilder(object):
    """
    Provides a simple interface for consistently building documentation.

    By default, this class will generate the API docs using sphinx's apidoc
    script, overwriting any existing API .rst files (provided the
    ``API_OUTPUT_DIR`` attribute has been set. Afterward, sphinx itself is run
    on the project.

    Projects are expected to create a file named ``build_docs.py`` (or
    something similar) within the ``docs`` directory of your project that
    contains a subclass of this class, instantiate it, then run its build
    method. An example::

        import os
        import sys

        THIS_DIR = os.path.dirname(__file__)
        sys.path.insert(0, os.path.join(THIS_DIR, '..', '..', 'src'))
        from granite.sphinx import DocBuilder


        def mkpath(*parts):
            \"\"\"Makes an abspath from THIS_DIR\"\"\"
            return os.path.normpath(os.path.join(THIS_DIR, *parts))


        class Builder(DocBuilder):
            # input path
            SOURCE_DIR = mkpath('source')
            # output path
            BUILD_DIR = mkpath('build')
            # remove this line if auto-api generation is not desired
            API_OUTPUT_DIR = mkpath('source', 'api')
            # the path to the python package
            PROJECT_DIR = mkpath('..', 'src', 'granite')

            FILES_TO_CLEAN = [
                API_OUTPUT_DIR,
                BUILD_DIR,
            ]


        if __name__ == '__main__':
            Builder().build()


    Each of the following attributes should be defined in order to configure
    DcoBuilder. Each attribute that is a path should be an absolute path.

    Attributes:
        SOURCE_DIR (str): the path to the project's source directory
        BUILD_DIR (str): the path to the documentation output
        API_OUTPUT_DIR (str): defining this will automatically call
                              sphinx-apidoc on the project directory. See the
                              generate_api_docs() method for more information.
                              *Optional*
        PROJECT_DIR (str): path to the directory containing Python project.
        FILES_TO_CLEAN (List[str]): a list of files to clean when ``--clean``
                                    is passed on the command line. *Optional*
        API_EXCLUDE_DIRS (List[str]): a list of paths relative to PROJECT_DIR
                                      to exclude from the api-doc generation.
    """
    SOURCE_DIR = ''
    BUILD_DIR = ''
    API_OUTPUT_DIR = ''
    PROJECT_DIR = ''
    API_EXCLUDE_DIRS = []

    FILES_TO_CLEAN = []

    def __init__(self):
        for attribute, description in (
                ('SOURCE_DIR',
                 'a path to the documentation source directory.'),
                ('BUILD_DIR', 'a directory place the built documentation.'),
                ('PROJECT_DIR',
                 'the path to the project package directory (the directory '
                 'containing the topmost __init__.py).'),
        ):
            if not getattr(self, attribute, None):
                raise RequiredAttributeException(
                    attribute, self.__class__, description)

        self.parser = argparse.ArgumentParser()
        self.args = None
        self.argv = []

    def safe_delete(self, filename):
        """
        Tries to delete ``filename`` and ignores any error that is raised.
        """
        try:
            os.remove(filename)
        except OSError:
            pass

    def generate_api_docs(self):
        """
        Generates the API documentation for all of the
        packages/modules/classes/functions.

        Sphinx doesn't automatically generate the documentation for the api.
        This calls sphinx-apidoc which will create the API .rst files and dump
        them in the source directory. It is expected that one of the TOC
        directives calls out to the created API directory.

        *Note:* if the attribute ``API_OUTPUT_DIR`` is not set on this class,
        then this method does nothing.
        """
        if self.API_OUTPUT_DIR:
            args = [
                # Put documentation for each module on its own page
                '-e',
                # don't create the "modules.rst" file (the table of contents
                # file) as this is already provided by the package's main rst
                # file.
                '-T',
                # Overwrite existing files
                '--force',
                '-o', self.API_OUTPUT_DIR,
                # the package to generate docs from
                self.PROJECT_DIR
            ]
            excludes = [
                os.path.join(self.PROJECT_DIR, p)
                if not os.path.isabs(p) else p
                for p in self.API_EXCLUDE_DIRS
            ]
            apidoc.main(args + excludes)

    def generate_documentation(self):
        """
        Runs sphinx on the project using the default conf.py file in the source
        directory.
        """
        self.generate_api_docs()
        build.main([
            self.SOURCE_DIR,
            self.BUILD_DIR,
        ])

    def try_clean(self):
        """
        Attempts to clean all of the files found in ``self.FILES_TO_CLEAN``.

        Ignores all errors.
        """
        for f in self.FILES_TO_CLEAN:
            if not os.path.exists(f):
                continue

            if os.path.isdir(f):
                # don't care on error
                shutil.rmtree(f, onerror=lambda *x, **y: None)
            else:
                self.safe_delete(f)

    def add_argument(self, *args, **kwargs):
        """
        Add an argument to the ArgumentParser in ``self.parser``.

        Takes in the same args and kwargs as the
        :meth:`ArgumentParser.add_argument` method. Use this method in order to
        add custom flags to the argument parsing. The argv flags are parsed in
        the ``build()`` method. This sets the parsed args into ``self.args``
        and the leftover unknown flags into ``self.argv``.
        """
        self.parser.add_argument(*args, **kwargs)

    def setup_default_arguments(self):
        """
        This method adds some default command line parameters.

        Current, the default flags are:

            - ``--clean``: Cleans all files found in the ``FILES_TO_CLEAN``
                list.
        """
        self.add_argument('--clean', action='store_true',
                          help='Cleans all generated files.')

    def pre_build_hook(self):
        """
        This is called after all arguments have been collected, but before
        sphinx is called.

        Override this method for any custom functionality.
        """

    def post_build_hook(self):
        """
        This is called immediately after all documentation has been generated.

        Override this method for any custom functionality.
        """

    def build(self, argv=None):
        """
        Gathers all command line arguments and then builds the docs.

        This performs command line parsing and stores the known flags (those
        added with ``self.add_argument()``) into ``self.args`` and all leftover
        unknown args into ``self.argv`` (see
        :meth:`argparse.ArgumentParser.parse_known_args` for more information
        on the types of each).

        After argparsing the following three methods are called in this order:

            * :meth:`pre_build_hook`
            * :meth:`generate_documentation`
            * :meth:`post_build_hook`

        Override the pre and post build hooks in order to add custom checks or
        other functionality.

        Args:
            argv (List[str]): command line flags to parse; defaults to sys.argv
        """
        if argv is None:
            argv = sys.argv

        self.setup_default_arguments()
        self.args, self.argv = self.parser.parse_known_args(argv)

        if self.args.clean:
            self.try_clean()

        self.pre_build_hook()
        self.generate_documentation()
        self.post_build_hook()
