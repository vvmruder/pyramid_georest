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

Configure the services which you want to be served via this api. Look at the following example to see how: 

```
   from pyramid_rest.lib.rest import Rest
   from pyramid_rest import prepare_models
   restful_services = [
      Rest(<your_engine>, <your_model>, <your_description_text>, <service_name>, <with_permission>),
      ...
   ]
   prepare_models(restful_services)
   config.include('pyramid_rest', route_prefix='api')
```
   
First you need to import the Rest class from the pyramid_rest package. This class is kind of a wrapper. It holds the configuration for the service, like the database connection in form of an sqlalchemy engine, the model which is the underlaying python-class-representation, and so on. Please see the class's documentation for further information. Once you have defined your service objects in a python list, you have to call the prepare_models method from this package. It is like a pre config of the package.

Add a "config.include('pyramid_rest', route_prefix='api')" line. This will include the rest api to your project and creates all the services as configured before.

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
