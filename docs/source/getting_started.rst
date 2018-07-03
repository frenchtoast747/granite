Developement - Getting Started
==============================

First and foremost, in order to develop on this project, you must work in a virtual
environment. A virtual environment (or virtualenv) in terms of Python development, is an
environment where the Python project can be developed, run, and tested such that global
or system environment doesn't interfere with the project environment. Each of the following
sections assume that you are working in the "dev" virtualenv.

Say you're working on a Python project that has a dependency on version 2 of package A. Also
assume that your global Python installation (on Windows, C:\Python27) has version 1 of
package A installed. Now, you could simply run ``pip install A==2.0`` and update your global
installation, but this may break some other package that isn't ready for version 2 of
package A. This is where virtualenvs come in to play. A virtualenv will have its own
Python executable, its own ``site-packages`` (where 3rd party packages are installed), its
own ``pip`` (Python package manager), and its own ``Scripts`` directory (where launcher
scripts are installed and are automatically added to the PATH). Thus completely isolating
the project's development environment from the system's.

We are using the Python package ``tox`` to manage our project's automation. ``tox`` manages
running the project in multiple virtualenvs. E.g., the project's tests can be run with
and without coverage, not only for Python 2.7, but also for Python 3.5, Python 3.6,
Python 3.x. ``tox`` can also be used to simply create a virtualenv and automatically install
packages that are needed by the project. For this project, this can be done by simply
issuing the command::

    tox -e dev

This will create the "dev" virtualenv (if it doesn't already exist) and install/update
and of the project's needed requirements. In order to work in this virtualenv, all that
is needed is to issue the activate command::

    source .tox/dev/Scripts/activate

for bash, and for CMD::

    .tox/dev/Scripts/activate.bat

This sets up the current shell to use that virtualenv. Running ``python`` from that shell
will use that virtualenv's Python executable which, in turn, will also use its PYTHONPATH,
Scripts, etc. To exit out of the virtualenv and drop back to the system's global environment
simply issue the following command for both CMD and bash::

    deactivate

Alternatively, you can close the shell and start a new one. Remember, working in a
virtualenv is shell-specific, so each new shell needs to activate the virtualenv directly.

Running Tests Directly
----------------------

Tests for this project are written using Python's builtin ``unittest`` module. Test
discovery and running is faciliated by ``nose2``. To run all of the tests, navigate to
the ``tests/`` directory and run the command::

    nose2

This will discover all test modules that start with ``test_`` and will run all methods
that start with ``test_`` of subclasses of ``unittest.TestCase``.

To run a single module/class/test method, pass the qualified Python name to that entity
as an argument to ``nose2``::

    nose2 package.module.test_feature.TestClass.test_that_something_happens_when_y_occurs


Running Tests With Tox
----------------------

``tox``'s main purpose is to run tests in multiple environments. Since Python 2.7 is no
longer being supported after 2020, we need to make sure that this project runs for both
Python2.7 and Python3.x. Tox makes this easy. Inside of the ``tox.ini`` file at the root
of the project is variable named ``envlist`` this is a list of environments to run tox
under. Simply running::

    tox

at the root of the project will run all of the environments. Currently, this will try to run
the tests with and without coverage for Python2.7, Python3.5, and Python3.6. The project is
also configured to fail a run with coverage if the coverage level drops below 100% (this
makes accepting third party code contributions easy to check since they can push to Jenkins
which will fail if any of the commands by tox fails). Additionally, coding style and Python
3 compatibility checks are performed. Pylint, Pylint --py3k, and pep8 are run against the
entire codebase. If any of these checks finds an error, tox will exit with a failure.
Lastly, the project's documentation is built.

To run all tests with a single environment, run ``tox`` with that environment's name::

    tox -e tests-py27-nocov

To see a list of all environment names, run ``tox`` with the -l flag (lowercase L)::

    tox -l

    tests-py27-nocov
    tests-py27-cov
    tests-py35-nocov
    tests-py35-cov
    tests-py36-nocov
    tests-py36-cov
    check-pylint
    check-pylint3
    check-pep8
    docs


To run a single test with a single environment, the ``tox.ini`` file has been set up to pass
any additional arguments on the command line to ``nose2``; simply pass any additional
``nose2`` arguments (like tests to run) after the ``-e`` flag::

    tox -e tests-py27-nocov test_something.TestClass.test_that_something_occurs


Building Documentation
----------------------

``tox`` can also be used to build the documentation. To do this, simply run::

    tox -e docs

This will build the documentation into a folder named ``build/`` in the ``docs/`` directory.
Inside of the ``build/`` directory is an HTML file named ``index.html``; this is the root
of the documentation.
