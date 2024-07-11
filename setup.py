#!/usr/bin/env python
from os import path
import re

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


# Find the package version in __init__.py without importing it
init_file = path.join(path.dirname(__file__), "monkeybiz", "__init__.py")
with open(init_file) as f:
    for line in f:
        m = re.search(r"""^__version__ = (['"])(.+?)\1$""", line)
        if m is not None:
            version = m.group(2)
            break
    else:
        raise LookupError("Unable to find __version__ in " + init_file)



setup(
    name='python-monkey-business',
    version=version,
    author='The Atlantic',
    author_email='programmers@theatlantic.com',
    url='https://github.com/theatlantic/python-monkey-business',
    description='Utility functions for monkey-patching python code',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=True,
    include_package_data=True,
    license="BSD",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ])
