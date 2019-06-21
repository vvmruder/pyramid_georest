.. _url_patterns:

Used URL patterns
=================

General hint
------------

The generated URL uses the API name to build unique name spaces. Please keep in mind that this API name is
combined with the route prefix of the included plugin if it was set:

* API with name 'api' without any route prefix for the plugin will result in 'api'
* API with name 'api' with a route prefix 'my_plugin' will result in 'my_plugin/api'

Access to multiple records reading
----------------------------------

.. code-block:: bash

    /<api name>/<schema_name>/<table_name>/read/<format>

This Endpoint accepts input on two different HTTP methods can be overwritten by Api class instantiation:

* read_method (default is GET). It simply delivers all records of the service.
* read_filter_method (default is POST). It delivers all records the service filtered. The filter must be
    submitted as json body content. Learn more about details of filtering here.

Both points accept the following URL parameter groups:

paging:

* offset
* limit

sorting:

* order_by
* direction

If only one of the parameter group members is submitted request will throw HTTP exception.
