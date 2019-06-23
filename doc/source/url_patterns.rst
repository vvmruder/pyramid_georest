.. _url_patterns:


Used URL patterns
=================


General hint
------------

The generated URL uses the API name to build unique name spaces. Please keep in mind that this API name is
combined with the route prefix of the included plugin if it was set:

* API with name 'api' without any route prefix for the plugin will result in 'api'
* API with name 'api' with a route prefix 'my_plugin' will result in 'my_plugin/api'


Overview
--------

.. list-table:: Entry points
    :header-rows: 1

    * - Entry point
      - HTTP Method (standard)
      - Comment
    * - /<api name>/<schema_name>/<table_name>/read/<format>
      - GET
      -
    * - /<api name>/<schema_name>/<table_name>/read/<format>
      - POST
      - Filter is passed as body content.
    * - /<api name>/<schema_name>/<table_name>/count/<format>
      - GET
      -
    * - /<api name>/<schema_name>/<table_name>/count/<format>
      - POST
      - Filter is passed as body content.
    * - /<api name>/<schema_name>/<table_name>/read/<format>/<primary_key>
      - GET
      -
    * - /<api name>/<schema_name>/<table_name>/create/<format>
      - POST
      - Feature is passed as body content.
    * - /<api name>/<schema_name>/<table_name>/update/<format>/<primary_key>
      - PUT
      - Feature is passed as body content.
    * - /<api name>/<schema_name>/<table_name>/delete/<format>/<primary_key>
      - DELETE
      -
    * - /<api name>/<schema_name>/<table_name>/model/<format>
      - GET
      -


Read multiple records
---------------------

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/read/<format>

This endpoint accepts input on two different HTTP methods (can be overwritten by Api class instantiation):

- read_method (default is GET). It simply delivers all records of the table.
- read_filter_method (default is POST). It delivers a filtered set of record filtered. The filter must be
  submitted as json body content. Learn more about details of :ref:`filter`.


Count records
-------------

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/count

This endpoint accepts input on two different HTTP methods (can be overwritten by Api class instantiation):

- read_method (default is GET). It simply counts all records of table.
- read_filter_method (default is POST). It counts all filtered records of the table. The filter must be
  submitted as json body content. Learn more about details of :ref:`filter`.


Read one record
---------------

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/read/<format>/<primary_key>

This endpoint accept input on HTTP GET method (default) and delivers the primary key matching record.

It is possible to have more then one primary key in a database table. So it is possible with this API too.
Simply pass all necessary primary keys like this:

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/read/<format>/<primary_key_1>/.../<primary_key_n>


Create one record
-----------------

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/create/<format>

This endpoint accepts input on HTTP POST method (default) and creates a record from data passed in body
of request. The structure has to be plain JSON with WKT string for geometric columns or GeoJSON. It must be
passed like this:

.. code-block:: javascript

    {
        "feature": {
            "id": 1,
            "geom": "POINT(1.00 2.00)"
        }
    }

or:

.. code-block:: javascript

    {
        "feature": {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [1.00, 2.00]
            },
            "properties": {
                "id": 1
            }
        }
    }


Update one record
-----------------

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/update/<format>/<primary_key>

This endpoint accepts input on HTTP PUT method (default) and updates a record from data passed in body
of request.

It is possible to have more then one primary key in a database table. So it is possible with this API too.
Simply pass all necessary primary keys like this:

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/update/<format>/<primary_key_1>/.../<primary_key_n>

The structure has to be plain JSON with WKT string for geometric columns or GeoJSON. It must be
passed like this:

.. code-block:: javascript

    {
        "feature": {
            "name": "Bud",
            "geom": "POINT(1.00 2.00)"
        }
    }

or:

.. code-block:: javascript

    {
        "feature": {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [1.00, 2.00]
            },
            "properties": {
                "name": "Bud"
            }
        }
    }


Update one record
-----------------

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/delete/<format>/<primary_key>

This endpoint accepts input on HTTP DELETE method (default) and deletes a record.

It is possible to have more then one primary key in a database table. So it is possible with this API too.
Simply pass all necessary primary keys like this:

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/delete/<format>/<primary_key_1>/.../<primary_key_n>


Obtain model description
------------------------

.. parsed-literal::

    /<api name>/<schema_name>/<table_name>/model/<format>

This endpoint offers a description of underlying data.
