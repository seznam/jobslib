
import sys

from pathlib import Path
from runpy import run_path

from setuptools import setup, find_packages

description = 'Library for launching tasks in parallel environment'

try:
    with open('README.rst', 'rt') as f:
        long_description = f.read()
except Exception:
    long_description = description

version_file = Path(__file__).parent / 'jobslib' / 'version.py'
if sys.version_info < (3, 6):
    version_file = str(version_file)
version = run_path(version_file)['VERSION']

setup(
    name='jobslib',
    version=version,
    author='Seznam.cz a.s.',
    author_email='doporucovani-vyvoj@firma.seznam.cz',
    description=description,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='BSD',
    url='https://github.com/seznam/jobslib.git',
    project_urls={
        'Documentation': 'https://seznam.github.io/jobslib/',
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        'cached-property',
        'colored',
        'influxdb',
        'objectvalidator',
        'python-consul2',
        'retrying',
    ],
    entry_points={
        'console_scripts': [
            'runjob = jobslib.main:main',
        ]
    },
)
