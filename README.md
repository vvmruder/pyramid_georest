Pyramid REST interface
======================

This little package gives shortcuts to create a restful api to database sources. It provides a url pattern to
serve the sources.
It is meant to be used in a pyramid web framework eco system. It uses pyramid and sqlalchemy logic as well.
Its goal is to extend the database usage in pyramid frameworks. This way, it will be possible to serve data
sources from different databases from a single pyramid application.
I used a simple class system to make this api as adaptable as possible.

Main features:

* read (json, geojson, xml) + filtering via json parameters - also for geographic attributes
* read one / show (json, geojson, xml)
* create one
* update one
* delete one
* data model description (json, geojson, xml) => This provides a description to implement client side forms
bound to the underlying data.

Special thing of this api: It can serve geometric extension objects too (It's only limited by geoalchemy2).

Dependencies:
=============
* pyramid (tested with 1.7.3)
* SQLAlchemy (tested with 1.0.15)
* GeoAlchemy2 (tested with 0.3.0)
* Shapely (tested with 1.5.17)
* dicttoxml (tested with 1.7.4)
* simplejson (tested with 3.8.2)


Usage in a standard pyramid web app
-----------------------------------

The pyramid framework for web apps provides an easy way for including
standalone packages in its eco system. To learn
more about that, please refer to the
[extending guide](http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/extending.html 'extending guide').

In a nutshell (inside the __init__.py of your pyramids project in the
main method ):

Configure the services which you want to be served via this api. Look
at the following example to see how:

```python
   from pyramid_georest.lib.rest import Api, Service
   from application.model import TestModel
   def main(global_config, **settings):
      """ This function returns a Pyramid WSGI application."""
      config = Configurator(settings=settings)
      config.include('pyramid_georest', route_prefix='api')
      test_api = Api(
         'postgresql://postgres:password@localhost:5432/test',
         config,
         'test_api'
      )
      test_service = Service(TestModel)
      test_api.add_service(test_service)
      config.scan()
      return config.make_wsgi_app()
```

Calling the config.include method with the package name will do some
initializing stuff (Note that the optional
parameter 'route_prefix' can be used to set the restful interface below
a fix name space. This may be helpful especially
in big applications).

Main concept
------------

The main goal of this library is to reduce the consumption of memory ,
url spaces and cpu usage. In big applications with a lot of services
this is a real big problem. In this context we have some central points
to take care of.

1. number of database connections
2. number of defined dedicated urls
3. adaptability of the several parts which a API consist of

Therefor this api ships with a mechanism which takes care of reusing
database connections as long as their definition is exactly the same
(we use the connections string for this as a key).
To reduce the number of constructed urls on server startup we create
only one set of restful urls per api. So every service added to an api
will fit in this set and will be identified by a match pattern.

Often you have some bigger applications and it is necessary to do some
more dedicated and more structured organization of api's.
Especially if you are using the possibility of pyramid plugins which
you include in the pyramid way ([pyramid include](http://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator.include 'pyramid include')).
This kind of api object creates its own url scope and will respect the
route_prefix of the including application. This is much more flexible
in big applications which have different scopes to use the rest api.
Of cause it is possible to have several levels of includes. All
combined route_prefixes will be taken into account.

**One dedicated API for a specific plugin**

If you have some plugin which you like to include in your pyramid
application (cause this is the most generic way you can extend pyramid)
you probably like to have a restful api dedicated to this plugin in
matter of url spaces and naming. The code to achieve this might look
like the following:

In your main pyramid application:

```python
   def main(global_config, **settings):
      """ This function returns a Pyramid WSGI application."""
      config = Configurator(settings=settings)
      config.include('pyramid_georest')
      config.include('my_plugin', route_prefix='my_plugin')
      config.scan()
      return config.make_wsgi_app()
```

In your plugins includeme mehtod:

```python
   from pyramid_georest.lib.rest import Api, Service
   from my_plugin.model import PluginModel
   def includeme(config):
      dedicated_api = Api(
         'postgresql://postgres:password@localhost:5432/test',
         config,
         'api'
      )
      dedicated_service = Service(PluginModel)
      dedicated_api.add_service(dedicated_service)
```

Please note also that the route prefix in the include method is not
mandatory but useful for the api created by this package.

Looking at the code above you will get an api which is running under
the prefix '/my_plugin/' and with the name 'api'.
So you will find each service bound to this api under /my_plugin/api/...
