import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def _get_version():
    filename = os.path.join(os.path.dirname(__file__), 'jobslib', 'CHANGELOG.md')
    with open(filename, 'rt') as fd:
        pat = r"""
            (?P<version>\d+\.\d+)         # minimum 'N.N'
            (?P<extraversion>(?:\.\d+)*)  # any number of extra '.N' segments
            (?:
                (?P<prerel>[abc]|rc)      # 'a' = alpha, 'b' = beta
                                          # 'c' or 'rc' = release candidate
                (?P<prerelversion>\d+(?:\.\d+)*)
            )?
            (?P<postdev>(\.post(?P<post>\d+))?(\.dev(?P<dev>\d+))?)?
        """
        for line in fd:
            match = re.search(pat, line, re.VERBOSE)
            if match:
                return match.group()
    raise ValueError("Can't get version")


__version__ = _get_version()


class PyTest(TestCommand):
    user_options = [
        ('pytest-args=', 'a', "Arguments to pass to py.test"),
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name="szn-recass-jobslib",
    version=__version__,
    author='Doporucovani team',
    author_email="doporucovani-vyvoj@firma.seznam.cz",
    description="Library for launching tasks in parallel environment",
    url='https://gitlab.kancelar.seznam.cz/doporucovani/recass',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
    packages=find_packages(include=['jobslib*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'cached-property',
        'colored<1.3',
        'python-consul',
        'ujson',
    ],
    tests_require=[
        'pytest-cov',
        'pytest',
    ],
    test_suite='tests',
    cmdclass={
        'test': PyTest,
    },
    entry_points={
        'console_scripts': [
            'runjob = jobslib.main:main',
        ]
    },
)
