Pyramid REST Changelog
======================

4.0.0
-----

* drop python 2 compatibility
* update dependencies

3.1.1
-----

* python version compatibility

3.1.0
-----

* Add build system
* Improve documentation
* Add testing

3.1.0-rc5
---------

* fix extensive logging on connection

3.1.0-rc4
---------

* fix paging which was called in wrong order for LIMIT and OFFSET
* implement sorting of one column via URL params _order_by_ and _direction_

3.1.0-rc3
---------

* fix filtering for non ascii charsets when LIKE is used

3.1.0-rc2
---------

* implement paging
* add count method to api

3.1.0-rc1
---------

* reorganizing service=>api structure
* cleaning methods
* minimize redundant code
* finalize inline documentation

3.0.34
------

* fix bug on geojson point and multipoint formatting

3.0.33
------

* fix bug in filter iteration

3.0.32
------

* improve code styling
* add python 3 compatibility

3.0.31
------

* add a commit to the configuration of the api

3.0.30
------

* fix url name spacing bug

3.0.29
------

* remove trailing print

3.0.28
------

* fix api naming bug

3.0.27
------

* fix import bug

3.0.26
------

* add route prefix to api names, they are unique per pyramid plugin then

3.0.25
------

* implement an easier way to extend the parmas of the adapter proxy
  which are sent to the template

3.0.24
------

* add not equals operator '!=' to filter

3.0.22
------

* remove default client side adapter, it is not useful to have it
  predefined

3.0.21
------

* implement the possibility to add client side adapters via mako
  templates
* remove the central api solution to avoid confusion, there are only
  stand alone api's from now

3.0.20
------

* set renderers under a more specific name space to avoid interferences
  with other plugins

3.0.19
------

* fix problem where the geometry was not set as valid value in
  update/create after flush

3.0.18
------

* deliver the persisted/deleted feature as response on update/create/delete

3.0.17
------

* implement correct export of geometry for polygons in geojson

3.0.16
------

* fix bug when rendering polygon types to geojson

3.0.15
------

* fix bug when creating multiple stand alone api's

3.0.14
------

* improve output for geojson format
* now it is possible to send data as geojson for create and update services

3.0.13
------

* handle NULL values for geometry

3.0.12
------

* set default value to None if it is a callable
* set srid automatically dependent on the model

3.0.11
------

* provide link between relationship and foreign key

3.0.10
------

* use srid from model definitions for write operations

3.0.9
-----

* change urls with primary keys

3.0.8
-----

* use a MANIFEST.in now

3.0.7
-----

* bugfix the problem that bad requests weren't catched and iteration
  over dict was not correctly implemented

3.0.6
-----

* bugfix to make the http methods for stand alone api configurable too

3.0.5
-----

* bugfix for add renderer problem, implement create, update, delete

3.0.4
-----

* implement a flag which makes it possible to create global and
  dedicated api's for more flexibility.

3.0.3
-----

* fix bug

3.0.2
-----

* fix the add_view problem when rest api is included in other
  applications.

3.0.1
-----

* fix the issue with geometric filtering
* make all geometric filter methods overwritable

3.0.0
-----

* redesign complete behaviour (straight classes for more flexibility)
* redesign url creation
* complete independent api creation

2.0.4
-----

Fixed issues:

* improve session handling
* use zope extension for sessions
* catch broad band errors to handle unknown behavior on db connections

2.0.3
-----

Fixed issues:

* [#2](https://github.com/vvmruder/pyramid_georest/issues/2): Fixed problem where the relationship properties
  wasn't loaded correctly .

2.0.2
-----

Fixed issues:

* [#2](https://github.com/vvmruder/pyramid_georest/issues/2): Fixed lost m to n handling.

2.0.1
-----

Fixed issues:

* [#1](https://github.com/vvmruder/pyramid_georest/pull/1): Fixed encoding issue in filter parameter.

2.0.0
-----

First usable version of this package (propably not pip save).

This version ships with the basic parts of REST and some updates which mainly belong to the sqlalchemy
session handling and the filtering system.
