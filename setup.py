#!/usr/bin/env python3
# This file is part of the sphinxcontrib-tryton extension.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from os.path import dirname, join
from re import compile, match
from setuptools import setup, find_packages


def read(fname):
    with open(join(dirname(__file__), fname), 'r', encoding='utf-8') as file:
        return file.read()


def version(fname):
    regex = compile("^version[^0-9]*([0-9A-Za-z_.-]*)")
    filename = join(dirname(__file__), fname, '__init__.py')
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            version = match(regex, line)
            if version:
                return version.group(1)


setup(
    name='sphinxcontrib-tryton',
    version=version('sphinxcontrib/tryton'),
    description=(
        "A Sphinx extension that enables better documentation of Tryton."),
    long_description=read('README.rst'),
    author='David Harper',
    author_email='python-packages@libateq.org',
    url='https://bitbucket.org/libateq/sphinxcontrib-tryton',
    project_urls={
        "Bug Tracker": (
            'https://bitbucket.org/libateq/sphinxcontrib-tryton/issues'),
        "Documentation": 'https://sphinxcontrib-tryton.readthedocs.org/',
        "Source Code": 'https://bitbucket.org/libateq/sphinxcontrib-tryton',
    },
    keywords='sphinx tryton documentation',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
    ],
    license='GPL-3',
    platforms='any',
    packages=find_packages(),
    namespace_packages=['sphinxcontrib'],
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'Sphinx>=2.0.0',
        'proteus>=5.0.0',
    ],
    # TODO: extras_require needs twine >= 1.11 to upload to PyPI
    # extras_require={
    #     'figure-tryton': [
    #         'tryton>=5.0.0',
    #     ],
    #     'figure-sao': [
    #         'pillow>=6.0.0',
    #         'selenium>=3.14.0'
    #     ],
    #     'local-trytond': ['trytond>=5.0.0'],
    #     'full-tests': [
    #         'pillow>=6.0.0',
    #         'selenium>=3.14.0'
    #         'tryton>=5.0.0',
    #         'trytond>=5.0.0',
    #         'trytond_account_credit_limit>=5.0.0',
    #         'trytond_currency>=5.0.0',
    #         'trytond_sale_stock_quantity>=5.0.0',
    #         'trytond_stock_lot_sled>=5.0.0',
    #     ],
    # },
    tests_require=[
        'sphinx-testing>=1.0.1',
    ],
    zip_safe=False,
)
