#!/usr/bin/env python
import os
import setuptools

PACKAGE = "janrain_datalib"

# get package version
HERE = os.path.abspath(os.path.dirname(__file__))
execfile(os.path.join(HERE, PACKAGE, "_version.py"))
# __version__ is now defined

setuptools.setup(
    name="janrain-python-datalib",
    description="Janrain Capture Data Library",
    version=__version__,
    url="https://github.com/janrain/janrain-python-datalib",
    packages=[
        PACKAGE,
    ],
    install_requires=[
        "janrain-python-api == 0.3.5",
    ],
    tests_require=[
        "Mock",
    ],
    test_suite="tests",
)
