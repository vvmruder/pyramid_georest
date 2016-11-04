Pyramid REST Changelog
======================

## 3.0.12

* set default value to None if it is a callable
* set srid automatically dependent on the model

## 3.0.11

* provide link between relationship and foreign key

## 3.0.10

* use srid from model definitions for write operations

## 3.0.9

* change urls with primary keys

## 3.0.8

* use a MANIFEST.in now

## 3.0.7

* bugfix the problem that bad requests weren't catched and iteration 
over dict was not correctly implemented

## 3.0.6

* bugfix to make the http methods for stand alone api configurable too 

## 3.0.5

* bugfix for add renderer problem, implement create, update, delete

## 3.0.4

* implement a flag which makes it possible to create global and 
dedicated api's for more flexibility.

## 3.0.3

* fix bug

## 3.0.2

* fix the add_view problem when rest api is included in other 
applications.

## 3.0.1

* fix the issue with geometric filtering
* make all geometric filter methods overwritable

## 3.0.0

* redesign complete behaviour (straight classes for more flexibility)
* redesign url creation
* complete independent api creation

## 2.0.4

Fixed issues:

* improve session handling
* use zope extension for sessions
* catch broad band errors to handle unknown behavior on db connections

## 2.0.3

Fixed issues:

* [#2](https://github.com/vvmruder/pyramid_georest/issues/2): Fixed problem where the relationship properties wasn't 
loaded correctly .

## 2.0.2

Fixed issues:

* [#2](https://github.com/vvmruder/pyramid_georest/issues/2): Fixed lost m to n handling.

## 2.0.1

Fixed issues:

* [#1](https://github.com/vvmruder/pyramid_georest/pull/1): Fixed encoding issue in filter parameter.

## 2.0.0

First usable version of this package (propably not pip save).

This version ships with the basic parts of REST and some updates which mainly belong to the sqlalchemy
session handling and the filtering system.
