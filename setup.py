import sys

from setuptools import setup

dependencies = [
    'jinja2>=2.10',
]

if sys.version_info <= (3, 0):
    dependencies.append('mock>=2.0')

setup(
    name='granite',
    description='Augments the unittest TestCase API by providing additional utilities useful for Python tools.',
    email='aaron@aaronboman.com',
    author='Aaron Boman',
    license='MIT',
    version='0.0.1',
    long_description=__doc__,
    packages=['granite'],
    include_package_data=True,
    zip_safe=True,
    install_requires=dependencies
)
