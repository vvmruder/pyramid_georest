# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2015, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
# All rights reserved.
#
# This program is free software and completes the GeoMapFish License for the geoview.bl.ch specific
# parts of the code. You can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
import os
from setuptools import setup, find_packages

__author__ = 'Clemens Rudert'
__create_date__ = '30.07.2015'

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov'
]

requires = [
    'pyramid',
    'SQLAlchemy',
    'shapely',
    'dicttoxml',
    'geoalchemy2',
    'transaction',
    'waitress',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'PyYAML',
    'psycopg2',
    'simplejson'
]

setup(
    name='pyramid_georest',
    version='3.1.0-rc2',
    description='pyramid_georest, extension for pyramid web frame work to provide rest interface for '
                'sql-alchemy mappers',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    license='GNU General Public License',
    author='Clemens Rudert',
    author_email='clemens.rudert@bl.ch',
    url='https://github.com/vvmruder/pyramid_georest',
    keywords='web pyramid pylons rest sqlalchemy orm model geoalchemy',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = pyramid_georest:main

    """,
)
