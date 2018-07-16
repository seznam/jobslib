import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from jobslib import __version__ as VERSION


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
    version=VERSION,
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
