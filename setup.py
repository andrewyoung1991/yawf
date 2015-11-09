import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from yawf import __version__


pyv = sys.version_info[:2]
if pyv < (3, 3):
    sys.exit("Sorry, Python 3.3 (with asyncio) or 3.4+ is required")


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        super().initialize_options()
        self.pytest_args = []

    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errono = pytest.main(self.pytest_args)
        sys.exit(errono)


def read(*, filename):
    base = os.path.dirname(__file__)
    contents = None
    with open(os.path.join(base, filename)) as _file:
        contents = _file.read()
    return contents

install = [
    "PyJWT==1.4.0",
    "websockets==2.6"
    ]

if pyv == (3, 3):
    install.append("asyncio")

tests = install + [
    "py==1.4.30",
    "coverage==4.0.1",
    "pytest==2.8.2",
    "pytest-cov==2.2.0",
    "pytest-cover==3.0.0",
    "pytest-coverage==0.0"
    ]

setup(
    name="yawf",
    version=__version__,
    author="Andrew Young",
    author_email="ayoung@thewulf.org",
    license="MIT",
    packages=find_packages(exclude=["tests", "examples"]),
    description="yeah, a websocket framework... for python.",
    long_description=read(filename="README.rst"),
    install_requires=install,
    tests_require=tests,
    cmdclass={"test": PyTest},
    entry_points={
        "console_scripts": [
            "yawf = yawf.commands:call_command"
            ]
        }
)
