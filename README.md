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

The pyramid framework for web apps provides an easy way for including standalone packages in its eco system. To learn
more about that, please refer to the http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/extending.html to
learn more about that.

In a nutshell (inside the __init__.py of your pyramids project in the main method ):

Configure the services which you want to be served via this api. Look at the following example to see how: 

```python
   from pyramid_rest.lib.rest import Rest
   from pyramid_rest import prepare
   restful_services = [
      Rest(<your_engine>, <your_model>, <your_description_text>, <service_name>, <with_permission>),
      ...
   ]
   prepare(restful_services)
   config.include('pyramid_rest', route_prefix='api')
```
   
First you need to import the Rest class from the pyramid_rest package. This class is kind of a wrapper. It holds the
configuration for the service, like the database connection in form of an sqlalchemy engine, the model which is the
underlaying python-class-representation, and so on. Please see the class's documentation for further information.
Once you have defined your service objects in a python list, you have to call the prepare_models method from this
package. It is like a pre config of the package. Once you defined all your restful services gather them in a python list
 and call the prepare method of this package. This provides your configuration to the package for later.

Calling the config.include method with the packages name will do some initializing stuff (Note that the optional
paramter 'route_prefix' can be used to set the restful interface below a fix name space. This may be helpful especially
in big applications.). Mainly it creates access to a standard documentation (once the Server is started it will be
available at .../<route_prefix>/pyramid_rest_doc or .../pyramid_rest_doc if route_prefix was not set).
In addition it creates all the urls/services which are needed.

Usage in a special geomapfish web app
-------------------------------------

Please refer to the original http://docs.camptocamp.net/c2cgeoportal/1.5/> of geomapfish to
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

Manage this package directly in your pyramid project folder as an subrepository. For that clone this repository to your projects home as follows:

.. code:: bash

   git clone https://github.com/vvmruder/pyramid_rest.git pyramid_rest

This way enables you to have two different versions running on the same server. This is very usefull when you have customers which are bound to the interface already. Then you can establish a new version of the api without break the old customers way of access. If you want that, act as follows:

.. code:: bash

   git clone https://github.com/vvmruder/pyramid_rest.git pyramid_rest_v1
   git clone https://github.com/vvmruder/pyramid_rest.git pyramid_rest_v2
   
```python
   from pyramid_rest_v1.lib.rest import Rest_v1
   from pyramid_rest_v2.lib.rest import Rest_v2
   from pyramid_rest_v1 import prepare as prepare_v1
   from pyramid_rest_v2 import prepare as prepare_v2
   
   restful_services_v1 = [
      Rest_v1(<your_engine>, <your_model>, <your_description_text>, <service_name>, <with_permission>),
      ...
   ]
   prepare_v1(restful_services)
   
   restful_services_v2 = [
      Rest_v2(<your_engine>, <your_model>, <your_description_text>, <service_name>, <with_permission>),
      ...
   ]
   prepare_v2(restful_services)
   config.include('pyramid_rest_v2', route_prefix='api/v2')
```
