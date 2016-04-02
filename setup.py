#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.0.1'

setup(
        name='qgis-egg',
        version='0.0.1',
        description='QGIS in an egg.',
        author='Bernhard Snizek',
        author_email='bernhard@septima.dk',
        maintainer='Bernhard Snizek',
        maintainer_email='bernhard@septima.dk',
        url='https://github.com/bsnizek/qgis-egg',
        license='Apache License 2.0',
        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7'
        ],
        include_package_data=True,
        platforms="Any",
        package_dir={'': 'src'},
        packages=find_packages('src'),
        namespace_packages=['qgis'],
        install_requires= [

        ],
        dependency_links=[

        ]
)
