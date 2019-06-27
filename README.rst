Pyramid GeoREST interface
=========================

pyramid_georest is a open source plugin for the pyramid web framework. It provides access to geographical
and (also non geographical) database sources via a restful API.

Are you tired of writing code to get some data out of a database to use it in some web client?

Wouldn't it be a good idea to be able to handle geodata and 'normal' data in one API?

Well... Then probably this library is exactly what you are looking for.

Its easy to install:

.. code-block: bash

  pip install pyramid_georest

Easy to setup:

.. code-block: python

  from pyramid_georest.lib.rest import Api, Service
  from application.model import YourSQLAlchemyModel
  # Or you can use a GeoAlchemy2Model as well
  
  def main(global_config, **settings):
     """ This function returns a Pyramid WSGI application."""
     config = Configurator(settings=settings)
     config.include('pyramid_georest', route_prefix='api')
     test_api = Api(
        'postgresql://postgres:password@localhost:5432/test',
        config,
        'test_api'
     )
     test_service = Service(YourSQLAlchemyModel)
     test_api.add_service(test_service)
     config.scan()
     return config.make_wsgi_app()

Run your pyramid application => Thats it!

To see your data point browser to:

.. parsed-literal:

  http://127.0.0.1:6543/test_api/schema_name/table_name/read/json

To learn more about this project and its abilities please refer to the detailed [documentation](https://vvmruder.github.io/pyramid_georest 'documentation').
