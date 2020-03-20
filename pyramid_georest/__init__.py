# -*- coding: utf-8 -*-

import logging
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationConflictError
from pyramid_georest.lib.renderer import RestfulJson, RestfulXML, RestfulModelJSON, RestfulModelXML, \
    RestfulGeoJson
from pyramid_mako import add_mako_renderer

log = logging.getLogger('pyramid_georest')

VERSION = "4.0.0"


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. This is necessary for development of
    your plugin. So you can run it local with the paster server and in a IDE like PyCharm. It
    is intended to leave this section as is and do configuration in the includeme section only.
    Push additional configuration in this section means it will not be used by the production
    environment at all!
    """
    config = Configurator(settings=settings)
    config.include('pyramid_georest', route_prefix='rest_api')
    config.scan()
    return config.make_wsgi_app()


def includeme(config):
    """
    By including this in your pyramid web app you can easily provide SQLAlchemy data sets via a restful API

    :param config: The pyramid apps config object
    :type config: Configurator
    """

    # bind the mako renderer to other file extensions
    try:
        add_mako_renderer(config, ".html")
        config.commit()
    except ConfigurationConflictError as e:
        log.debug('Renderer for "html" already exists: {0}'.format(e.message))
    try:
        add_mako_renderer(config, ".js")
        config.commit()
    except ConfigurationConflictError as e:
        log.debug('Renderer for "js" already exists: {0}'.format(e.message))

    # add standard renderers
    config.add_renderer(name='geo_restful_json', factory=RestfulJson)
    config.add_renderer(name='geo_restful_geo_json', factory=RestfulGeoJson)
    config.add_renderer(name='geo_restful_xml', factory=RestfulXML)
    config.add_renderer(name='geo_restful_model_json', factory=RestfulModelJSON)
    config.add_renderer(name='geo_restful_model_xml', factory=RestfulModelXML)

    # add request attributes

    # global database connection holder see database script/rest script in api class
    # this feature is mainly used to reduce open database connections. They will be shared if they are exactly
    # the same.
    config.registry.pyramid_georest_database_connections = {}
    # global api holder
    config.registry.pyramid_georest_apis = {}
    # place where the api is available on each request
    config.registry.pyramid_georest_requested_api = None
    # place where the service is available on each request
    config.registry.pyramid_georest_requested_service = None
