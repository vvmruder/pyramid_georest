.. _filter:

Filtering
=========

pyramid_georest implements a really powerful filter system to provide even deep nested filter combination
possibilities.

Some of these abilities should be shown here to show you how this works and how you can take the best effort
out of it into your own application using this API.

Prerequisites
-------------

For all example given below we assume your API is configured to be available under the following url path:

.. note::

    <application host>/api/test_schema/test_table

This means you initialized your API with the name *api* without any route prefix on including. Your database
table *test_table* is situated in the database schema *test_schema*.

Sorting and paging
------------------

The API offers a way to implement paging in your application using this API. This is possible by passing the
*offset* and *limit* both as url parameters whether to the read all or the read with filter url endpoint:

.. note::

    <application host>/api/test_schema/test_table/read.json?offset=0&limit=10

Unsurprisingly this will deliver the first 10 matches of the bound resource.

If you want to used something like paging in your application you can "swipe" through the collection of your
database records with manipulating the described parameters. Let's assume you have a table in your
application which should show only 10 records at a time for performance reason and offers a selector to
switch between this 10-record-windows via paging. You only need to set parameter like this:

.. note::

    <application host>/api/test_schema/test_table/read.json?offset=0&limit=10 # page 1
    <application host>/api/test_schema/test_table/read.json?offset=10&limit=20 # page 2
    <application host>/api/test_schema/test_table/read.json?offset=20&limit=30 # page 3

    ...

.. note::

    It is mandatory to provide both. The offset and the limit parameter. Anything else will throw an error.

In addition to the option of windowing/paging you have the ability to sort your data by **one** column in a
selectable direction. This can be done by passing *order_by* and *direction* both as url parameters like this:

.. note::

    <application host>/api/test_schema/test_table/read.json?order_by=test_column&direction=asc # ascending
    <application host>/api/test_schema/test_table/read.json?order_by=test_column&direction=desc # descending

.. note::

    It is possible to pass these six types of direction directives:

    * ASC
    * asc
    * ascending
    * DESC
    * desc
    * descending

    everything else will throw an error.

.. note::

    **Of course sorting and paging is fully combinable.**


Simple filters
--------------
