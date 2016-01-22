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
from .lib.renderer import RestfulJson, RestfulXML, RestfulModelJSON, RestfulModelXML
from pyramid_rest.lib.rest import Rest
from pyramid.renderers import JSONP

__author__ = 'Clemens Rudert'
__create_date__ = '23.07.2015'

restful_models = []

_READ = 'GET'
_UPDATE = 'PUT'
_CREATE = 'POST'
_DELETE = 'DELETE'

additional_mappers = []


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
    if settings.get("default_max_age") is not None:
        config.add_static_view('pyramid_rest', 'pyramid_rest:static',
            cache_max_age=int(config.get_settings()["default_max_age"])
        )
    else:
        config.add_static_view('pyramid_rest', 'pyramid_rest:static', cache_max_age=3600)
    config.add_route('pyramid_rest_doc', '')
    config.add_view(
        'pyramid_rest.views.doc',
        renderer='pyramid_rest:templates/doc.mako',
        route_name='pyramid_rest_doc'
    )
    config.add_renderer('jsonp', JSONP(param_name='callback'))
    config.add_renderer(name='restful_json', factory=RestfulJson)
    config.add_renderer(name='restful_xml', factory=RestfulXML)
    config.add_renderer(name='model_restful_json', factory=RestfulModelJSON)
    config.add_renderer(name='model_restful_xml', factory=RestfulModelXML)
    config.registry.pyramid_rest_services = []
    if settings.get('pyramid_rest_support_mail') is not None:
        config.registry.pyramid_rest_support_mail = settings.get('pyramid_rest_support_mail')
    else:
        config.registry.pyramid_rest_support_mail = 'NO SUPPORT MAIL ADRESS WAS SET IN THE USED *.INI FILE'
    if settings.get('pyramid_rest_support_name') is not None:
        config.registry.pyramid_rest_support_name = settings.get('pyramid_rest_support_name')
    else:
        config.registry.pyramid_rest_support_name = 'NO SUPPORT MAIL ADRESS WAS SET IN THE USED *.INI FILE'

    _READ = settings.get('rest_read_http_method') if settings.get('rest_read_http_method') is not None else 'GET'
    _UPDATE = settings.get('rest_update_http_method') if \
        settings.get('rest_update_http_method') is not None else 'PUT'
    _CREATE = settings.get('rest_create_http_method') if settings.get('rest_create_http_method') is not None else 'POST'
    _DELETE = settings.get('rest_delete_http_method') if \
        settings.get('rest_delete_http_method') is not None else 'DELETE'

    # note: this creates all restful services if they where configured before the include method was called. Maybe there
    # a more elegant way for that. But this seems the only way to provide the passed route_prefix to the restful urls
    # also.
    for restful_model in restful_models:
        restful_model.bind(config)