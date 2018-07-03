import os
import sys

from granite.sphinx import DocBuilder

THIS_DIR = os.path.dirname(__file__)


def mkpath(*parts):
    """Makes an abspath from THIS_DIR"""
    return os.path.normpath(os.path.join(THIS_DIR, *parts))


class Builder(DocBuilder):
    # input path
    SOURCE_DIR = mkpath('source')
    # output path
    BUILD_DIR = mkpath('build')
    # the path to the python package
    PROJECT_DIR = mkpath('..', 'granite')
    API_OUTPUT_DIR = mkpath('source', 'api')

    FILES_TO_CLEAN = [
        BUILD_DIR,
    ]


if __name__ == '__main__':
    Builder().build()
