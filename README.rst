Pyramid REST interface
======================

This little package gives shortcuts to create a restful api to database sources. It provides a url pattern to serve the
sources.
It is meant to be used in a pyramid web framework ecosystem. It uses pyramid and sqlalchemy logic as well. Its goal is
to extend the database usage in pyramid frameworks. This way, it will be possible to serve different data sources from
different databases.

Main features:
* read (json, xml, geojson) + filtering via json parameters
* count  + filtering via json parameters
* read one (json, xml, geojson)
* create
* update
* delete
* data model description (json, xml)

Special thing of this api: It can serve geometric extension objects too (PostGIS at this time).

Usage in a standard pyramid web app
-----------------------------------

TODO

Usage in a special geomapfish web app
-------------------------------------

TODO

Configuration in the including apps *.ini files
-----------------------------------------------

Possible parameters are:

* pyramid_rest_support_mail => This will be used as mail adress in HTML documents created by the REST-API
* pyramid_rest_support_name => This will be used as alias in HTML documents created by the REST-API

Read the `Documentation <(LINK TO THE DOC)>`_

Checkout
--------

.. code:: bash

   git clone https://github.com/vvmruder/pyramid_rest.git pyramid_rest