#!/usr/bin/env python
import os
import setuptools

# get package version
PACKAGE = "janrain_datalib"
HERE = os.path.abspath(os.path.dirname(__file__))
VERSIONFILE = os.path.join(HERE, PACKAGE, "_version.py")
exec(compile(open(VERSIONFILE).read(), VERSIONFILE, 'exec'))
# __version__ is now defined

setuptools.setup(
    name="janrain-datalib",
    description="Janrain Capture Data Library",
    version=__version__,
    url="https://github.com/janrain/janrain-python-datalib",
    packages=[
        PACKAGE,
    ],
    install_requires=[
        "janrain-python-api == 0.4.0",
    ],
    tests_require=[
        "Mock",
    ],
    test_suite="tests",
)
