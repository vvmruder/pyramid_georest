# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from pyramid_georest import VERSION

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
    'GeoAlchemy2',
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
    version=VERSION,
    description='pyramid_georest, extension for pyramid web frame work to provide rest interface for '
                'sql-alchemy mappers',
    long_description=README + '\n\n' + CHANGES,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
