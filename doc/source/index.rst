.. pyramid_georest documentation master file, created by
   sphinx-quickstart on Tue May 28 13:32:02 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :caption: Contents:
   :hidden:

   usage
   url_patterns
   filter
   main_classes
   special_classes

pyramid_georest documentation
=============================

This little package gives shortcuts to create a restful api to database sources. It provides a url pattern to
serve the sources.
It is meant to be used in a pyramid web framework eco system. It uses pyramid and sqlalchemy logic as well.
Its goal is to extend the database usage in pyramid frameworks. This way, it will be possible to serve data
sources from different databases from a single pyramid application.

I used a simple class system to make this api as adaptable as possible.

Main features:

* read (json, geojson, xml) + filtering via json parameters - also for geographic attributes + paging
* read one / show (json, geojson, xml)
* create one
* update one
* delete one
* data model description (json, geojson, xml) => This provides a description to implement client side forms
  bound to the underlying data.

Special thing of this api: It can serve geometric extension objects too (It's only limited by geoalchemy2).

Main concept
------------

The main goal of this library is to reduce the consumption of memory ,
url spaces and cpu usage. In big applications with a lot of services and therefor many incoming requests
this is a really big problem. In this context we have some central points
to take care of.

1. number of database connections
2. number of defined dedicated urls
3. adaptability of the several parts which a API consist of

Therefor this api ships with a mechanism which takes care of reusing
database connections as long as their definition is exactly the same
(we use the connections string for this as a key).
To reduce the number of constructed urls on server startup we create
only one set of restful urls per api. So every service added to an api
will fit in this set and will be identified by a match pattern. If you are interested more in detail, please
have a closer look in :ref:`url_patterns`

**To explain it in a more schematic way:**

pyramid_georest defines a API object per unique database connection string and holds them in a dictionary by
name as identifier. The *registration* is done on startup. So you will get an error on application start if
there is a name interference between several registered API's.
Each API holds arbitrary number of Service classes which represents the entry points for the CRUD interface.

Often you have some bigger applications and it is necessary to do some
more dedicated and more structured organization of api's.
Especially if you are using the possibility of pyramid plugins which
you include in the pyramid way ([pyramid include](http://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator.include 'pyramid include')).
This kind of api object creates its own url scope and will respect the
route_prefix of the including application. This is much more flexible
in big applications which have different scopes to use the rest api.
Of cause it is possible to have several levels of includes. All
combined route_prefixes will be taken into account.

One dedicated API for a specific plugin
.......................................

If you have some plugin which you like to include in your pyramid
application (cause this is the most generic way you can extend pyramid)
you probably like to have a restful api dedicated to this plugin in
matter of url spaces and naming. The code to achieve this might look
like the following:

In your main pyramid application:

.. code-block:: python

   def main(global_config, **settings):
      """ This function returns a Pyramid WSGI application."""
      config = Configurator(settings=settings)
      config.include('pyramid_georest')
      config.include('my_plugin', route_prefix='my_plugin')
      config.scan()
      return config.make_wsgi_app()

In your plugins includeme mehtod:

.. code-block:: python

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

Please note also that the route prefix in the include method is not
mandatory but useful for the api created by this package.

Looking at the code above you will get an api which is running under
the prefix '/my_plugin/' and with the name 'api'.
So you will find each service bound to this api under /my_plugin/api/...

Some words about pyramid's plugin system
........................................

Obviously this system is really flexible. And that's why it is completely possible there might be a situation
where the approach of registering API's might fail. You only need do think of a main application which
includes several plugins using pyramid_georest which them self include plugins which are using
pyramid_georest.

I'am interested in such use cases and I will try to do my best to solve bugs on that. But sometimes the more
generic approach also might be a reorganisation of the code in such projects (own experience).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
