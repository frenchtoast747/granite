import os
import sys

from setuptools import setup

dependencies = [
    'jinja2>=2.10',
]

if sys.version_info < (3, 0):
    dependencies.append('mock>=2.0')

if sys.version_info < (3, 4):
    dependencies.append('pathlib2>=2.3')

readme = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')

with open(readme, 'r') as f:
    long_description = f.read()

setup(
    name='granite',
    description='Augments the unittest TestCase API by providing additional utilities useful for Python tools.',
    author_email='aaron@aaronboman.com',
    author='Aaron Boman',
    license='MIT',
    url='https://github.com/frenchtoast747/granite',
    version='0.0.4',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['granite'],
    include_package_data=True,
    zip_safe=True,
    install_requires=dependencies,
    classifiers=(
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Testing :: Unit',
        'Topic :: Utilities',
    ),
)
