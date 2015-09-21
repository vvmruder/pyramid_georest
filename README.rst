Pyramid REST interface
======================

This little package gives shortcuts to create a restful api to database sources. It provides a url pattern to serve the
sources.
It is meant to be used in a pyramid web framework eco system. It uses pyramid and sqlalchemy logic as well. Its goal is
to extend the database usage in pyramid frameworks. This way, it will be possible to serve data sources from
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

The pyramid framework for web apps provides an easy way for including standalone packages in its eco system. To learn more about that, please refer to the `pyramid documentation <http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/extending.html>`_ to learn more about that.

In a nutshell (inside the __init__.py of your pyramids project in the main method ):

1. configure the services which you want to be served via this api. Look at the following example to see how: 

```python
from pyramid_rest.lib.rest import Rest

print s
```

2. add a "config.include('pyramid_rest', route_prefix='api')" line. This will include the rest api to your project and creates all the services as configured before.

Usage in a special geomapfish web app
-------------------------------------

Please refer to the original `Documentation <http://docs.camptocamp.net/c2cgeoportal/1.5/>`_ of geomapfish to
learn more about this package.

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
