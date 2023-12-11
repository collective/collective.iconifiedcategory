# -*- coding: utf-8 -*-
"""Installer for the collective.iconifiedcategory package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read() +
    '\n' +
    'Contributors\n' +
    '============\n' +
    '\n' +
    open('CONTRIBUTORS.rst').read() +
    '\n' +
    open('CHANGES.rst').read() +
    '\n')


setup(
    name='collective.iconifiedcategory',
    version='0.62',
    description="An add-on for Plone",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='IMIO',
    author_email='support@imio.be',
    url='https://pypi.python.org/pypi/collective.iconifiedcategory',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'collective.documentviewer<5',
        'collective.eeafaceted.z3ctable>2.17',
        'collective.fontawesome>=1.1',
        'collective.js.tooltipster>0.1',
        'collective.z3cform.select2',
        'imio.helpers',
        'natsort',
        'plone.api>=1.4.11',
        'plone.app.contenttypes',
        'plone.app.dexterity',
        'plone.autoform',
        'plone.formwidget.namedfile',
        'plone.namedfile',
        'setuptools',
        'z3c.jbot',
        'z3c.json',
        'z3c.table',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
