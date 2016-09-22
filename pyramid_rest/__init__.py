# -*- coding: iso-8859-1 -*-

# Copyright (c) 2012 - 2015, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
# All rights reserved.
#
# This program is free software and completes the GeoMapFish License for the geoview.bl.ch specific
# parts of the code. You can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from pyramid_mako import add_mako_renderer

from pyramid_rest.lib.renderer import RestfulJson, RestfulXML, RestfulModelJSON, RestfulModelXML, RestfulGeoJson

__author__ = 'Clemens Rudert'
__create_date__ = '23.07.2015'

restful_models = []

_READ = 'GET'
_UPDATE = 'PUT'
_CREATE = 'POST'
_DELETE = 'DELETE'

additional_mappers = []


def main(global_config, **settings):
    from pyramid_rest.lib.database import Connection
    from pyramid_rest.lib.rest import Api, Service
    from pyramid_rest.models import Test
    """ This function returns a Pyramid WSGI application. This is necessary for development of
    your plugin. So you can run it local with the paster server and in a IDE like PyCharm. It
    is intended to leave this section as is and do configuration in the includeme section only.
    Push additional configuration in this section means it will not be used by the production
    environment at all!
    """
    config = Configurator(settings=settings)
    config.include('pyramid_rest')
    test_api = Api(
        'postgresql://postgres:password@localhost:5432/gdwh',
        config,
        'test'
    )
    test_service = Service(Test, 'av_admin', 'v_gemeindegrenze', ['gemgr_id'], test_api)
    test_api.add_service(test_service)
    config.scan()
    return config.make_wsgi_app()


def prepare(rest_services):
    """

    :param rest_services: a list with the configured rest objects
    :type rest_services: list of Rest
    """
    global restful_models
    restful_models = rest_services


def includeme(config):
    """
    By including this in your pyramid web app you can easily provide SQLAlchemy data sets via a restful API

    :param config: The pyramid apps config object
    :type config: Configurator
    """
    global _CREATE, _DELETE, _READ, _UPDATE

    settings = config.get_settings()

    config.include('pyramid_mako')

    # bind the mako renderer to other file extensions
    add_mako_renderer(config, ".json")

    config.include('pyramid_rest.routes')
    config.add_renderer(name='restful_json', factory=RestfulJson)
    config.add_renderer(name='restful_geo_json', factory=RestfulGeoJson)
    config.add_renderer(name='restful_xml', factory=RestfulXML)
    config.add_renderer(name='model_restful_json', factory=RestfulModelJSON)
    config.add_renderer(name='model_restful_xml', factory=RestfulModelXML)
    config.registry.pyramid_rest_database_connections = {}
    config.registry.pyramid_rest_apis = {}
    config.registry.pyramid_rest_services = []
    if settings.get('pyramid_rest_support_mail') is not None:
        config.registry.pyramid_rest_support_mail = settings.get('pyramid_rest_support_mail')
    else:
        config.registry.pyramid_rest_support_mail = 'NO SUPPORT MAIL ADRESS WAS SET IN THE USED *.INI FILE'
    if settings.get('pyramid_rest_support_name') is not None:
        config.registry.pyramid_rest_support_name = settings.get('pyramid_rest_support_name')
    else:
        config.registry.pyramid_rest_support_name = 'NO SUPPORT MAIL ADRESS WAS SET IN THE USED *.INI FILE'
