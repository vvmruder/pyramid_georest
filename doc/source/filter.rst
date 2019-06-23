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

.. parsed-literal::

    <application host>/api/test_schema/test_table

This means you initialized your API with the name *api* without any route prefix on including. Your database
table *test_table* is situated in the database schema *test_schema*.


Sorting and paging
------------------

The API offers a way to implement paging in your application using this API. This is possible by passing the
*offset* and *limit* both as url parameters whether to the read all or the read with filter url endpoint:

.. parsed-literal::

    <application host>/api/test_schema/test_table/read.json?offset=0&limit=10

Unsurprisingly this will deliver the first 10 matches of the bound resource.

If you want to used something like paging in your application you can "swipe" through the collection of your
database records with manipulating the described parameters. Let's assume you have a table in your
application which should show only 10 records at a time for performance reason and offers a selector to
switch between this 10-record-windows via paging. You only need to set parameter like this:

.. parsed-literal::

    <application host>/api/test_schema/test_table/read.json?offset=0&limit=10 # page 1
    <application host>/api/test_schema/test_table/read.json?offset=10&limit=20 # page 2
    <application host>/api/test_schema/test_table/read.json?offset=20&limit=30 # page 3
    ...

.. note::

    It is mandatory to provide both. The offset and the limit parameter. Anything else will throw an error.

In addition to the option of windowing/paging you have the ability to sort your data by **one** column in a
selectable direction. This can be done by passing *order_by* and *direction* both as url parameters like this:

.. parsed-literal::

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

    **Of course sorting and paging is can be combined.**

This mechanism is applied to the normal *read entry point* and also to the *filtered read entry point* (see
:ref:`url_patterns` for details).


General filter structure
------------------------

.. note::

    Filtering mechanism is done through the **HTTP POST** method. So API expects the filter parameters to be
    passed as **JSON in the body** of the request. The most important reason for this is to prevent
    limitations of URL length which will surely be scratched on complex filters with geometry content.

The filter system tries to keep the logic of SQL in some way and transport it to a web usable language. This
is JSON. As you can see below the general filter system is a JSON structure which defines a filter by setting
the *mode* to be used for combining the elements stored in the array of clauses. The mode is whether *AND* or
*OR*.

.. code-block:: javascript

    {
      'filter': {
        'definition': {
          'mode': 'AND',
          'clauses': []
        }
      }
    }

The clause array can contain a filter definition itself. That's how you can implement fairly complex filters.

A clause is a JSON-Object constructed 3 attributes:

* *column_name* is the desired column name of your database model.
* *operator* is the logical operator which is a bit varying on the type of the column you try to filter.
  On generic types like string or number types it provides the following options (please scroll also right
  table is a little big):

  +-----------------+------------------------+-----------------------------+----------------------------+
  | **operator**    | **meaning**            | **value**                   | **notes**                  |
  +=================+========================+=============================+============================+
  | *==*            | equals                 | string or number types      |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *=*             | equals                 | string or number types      |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *<>*            | not equals             | string or number types      |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *!=*            | not equals             | string or number types      |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *<*             | less than              | string or number types      | be aware in case of string |
  +-----------------+------------------------+-----------------------------+ types the behaviour        |
  | *<=*            | less than or equals    | string or number types      | completely depends on the  |
  +-----------------+------------------------+-----------------------------+ underling database and     |
  | *>*             | greater than           | string or number types      | encoding                   |
  +-----------------+------------------------+-----------------------------+                            |
  | *>=*            | greater than or equals | string or number types      |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *LIKE*          | SQL LIKE               | string with possible        | this will cast database    |
  |                 |                        | wildcards *%* and *_* for   | value to string for        |
  |                 |                        | instance 'Ab%' or 'a__%'    | comparison                 |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *IN*            | SQL IN                 | comma separated string like |                            |
  |                 |                        | 'Bud,Terence' or '1,2,3'    |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *NULL*          | SQL IS NULL            | *null* or anything it won't |                            |
  |                 |                        | be interpreted              |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *NOT NULL*      | SQL IS NOT NULL        | *null* or anything it won't |                            |
  |                 |                        | be interpreted              |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | **Geometric operators**                                                                             |
  +-----------------+------------------------+-----------------------------+----------------------------+
  | *INTERSECTS*    | eg. ST_Intersects in   | any WKT compatible geometry | **Only PostGIS is          |
  |                 | PostGIS                |                             | supported in the moment!** |
  +-----------------+------------------------+                             |                            |
  | *TOUCHES*       | eg. ST_Touches in      |                             | I would be glad to support |
  |                 | PostGIS                |                             | other DB's too. Please     |
  +-----------------+------------------------+                             | contact me or file an      |
  | *COVERED_BY*    | eg. ST_CoveredBy in    |                             | issue.                     |
  |                 | PostGIS                |                             |                            |
  +-----------------+------------------------+                             |                            |
  | *WITHIN*        | eg. ST_DFullyWithin in |                             |                            |
  |                 | PostGIS                |                             |                            |
  +-----------------+------------------------+-----------------------------+----------------------------+
* *value* is the value which should be used to compare against database

.. note::

    A word about the geometric filtering. In the moment this API should support every WKT compatible geometry
    type. Even geometry collections => they are extracted arbitrary deep and the filter is assigned to every
    single element of collection. If you encounter any problem don't hesitate to file an issue.


Simple filters
--------------

Construction of filter is easy. Below you can see a simple match filter which should return all matches for
id equals 1 assuming id is a number field.

.. code-block:: javascript

    {
      'filter': {
        'definition': {
          'mode': 'AND',
          'clauses': [{
            'column_name': 'id',
            'operator': '==',
            'value': 1
          }]
        }
      }
    }

.. note::

    Above the mode AND is used. Obviously this has no effect since we only define one clause. So in this case
    it doesn't matter if we pass *AND* or *OR*. But mode is mandatory always. So omitting it will throw an
    error.

.. code-block:: javascript

    {
      'filter': {
        'definition': {
          'mode': 'OR',
          'clauses': [{
            'column_name': 'id',
            'operator': '==',
            'value': 1
          }]
        }
      }
    }

Regarding to the note above this filter should produce the same result as the *AND* version.


Geometric filters
-----------------

Creating a geometric filter is easy as the filters for string or number types. Keep in mind the geometric
operators which are available in the moment. For details see table above.

The value has to be a string of valid WKT. Without any spatial reference system. This means the API is not
transforming any input. Your input of geometry WKT has to be in the same projection like your database
geometries are.

.. code-block:: javascript

    {
      'filter': {
        'definition': {
          'mode': 'AND',
          'clauses': [{
            'column_name': 'geom',
            'operator': 'INTERSECTS',
            'value': 'POINT(2615051.0 1264822.5)'
          }]
        }
      }
    }

Of cause you can combine string/number filters with geometric filters in any way. In the example below both
clauses are logically connected the *AND*.

.. code-block:: javascript

    {
      'filter': {
        'definition': {
          'mode': 'AND',
          'clauses': [{
            'column_name': 'geom',
            'operator': 'INTERSECTS',
            'value': 'POINT(2615051.0 1264822.5)'
          },{
            'column_name': 'type',
            'operator': '==',
            'value': 'building'
          }]
        }
      }
    }


Complex nested filters
----------------------

Sooner or later you will come to the point where simple one mode filters aren't enough. Then you can start to
nest filters to get even more tuned selection.

.. code-block:: javascript

    {
      "filter": {
        "definition": {
          "mode": "AND",
          "clauses": [
            {
              "mode": "OR",
              "clauses": [
                {
                  "column_name": "geom",
                  "operator": "INTERSECTS",
                  "value": "POINT(2615051.0 1264822.5)"
                },
                {
                  "column_name": "geom",
                  "operator": "INTERSECTS",
                  "value": "POINT(2618963.0 1263219.0)"
                }
              ]
            },
            {
              "column_name": "id",
              "operator": ">",
              "value": 2800
            }
          ]
        }
      }
    }

It is only necessary to put a object inside clauses which defines a mode again which is then assigned to the
sub clauses. So here a simple *AND* connection is done between the clause *id is greater than 2800* and the
sub clauses. The sub clauses are connected as *OR*.
