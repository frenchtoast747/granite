"""
Provides utilities for handling I/O during test excution.
"""
from __future__ import absolute_import

import contextlib
import sys

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


@contextlib.contextmanager
def capture_output():
    """
    Captures both stdout and stderr and stores into a string buffer.

    Example::

        import sys

        with capture_output() as (stdout, stderr):
            stdout = 'This is stdout'
            stderr = 'This is stderr'

            print(stdout)
            assert stdout.getvalue() == stdout.strip()

            sys.stderr.write(stderr)
            assert stderr.getvalue() == stderr
    """
    with capture_stdout() as stdout, capture_stderr() as stderr:
        yield stdout, stderr


@contextlib.contextmanager
def capture_stdout():
    """
    Captures stdout and stores in a string buffer.

    Example::

        with capture_stdout() as stdout:
            stdout = 'Hello, World!
            print(stdout)
            assert stdout.getvalue() == stdout.strip()

    The yielded value is a StringIO buffer. See its documentation for more
    details.
    """
    sys.stdout = StringIO()
    yield sys.stdout
    sys.stdout = sys.__stdout__


@contextlib.contextmanager
def capture_stderr():
    """
    Captures stderr and stores in a string buffer.

    Example::

        with capture_stderr() as stderr:
            stderr = 'Hello, World!
            print(stderr)
            assert stderr.getvalue() == stderr.strip()

    The yielded value is StringIO buffer. See its documentation for more
    details.
    """
    sys.stderr = StringIO()
    yield sys.stderr
    sys.stderr = sys.__stderr__
