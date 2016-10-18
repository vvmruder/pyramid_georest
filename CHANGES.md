Pyramid REST Changelog
======================

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
