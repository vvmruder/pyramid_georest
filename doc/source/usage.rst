.. _usage:

Usage
=====

The pyramid framework for web apps provides an easy way for including
standalone packages in its eco system. To learn more about that, please refer to the
[extending guide](http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/extending.html 'extending guide').

In a nutshell (inside the __init__.py of your pyramids project in the
main method ):

Configure the services which you want to be served via this api. Look
at the following example to see how:

.. code-block:: python

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


Calling the config.include method with the package name will do some
initializing stuff (Note that the optional
parameter 'route_prefix' can be used to set the restful interface below
a fix name space. This may be helpful especially
in big applications).
