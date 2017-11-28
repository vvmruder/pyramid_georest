# -*- coding: utf-8 -*-

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
import decimal
import simplejson
import datetime
import logging

import dicttoxml
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from pyramid.httpexceptions import HTTPNotFound, HTTPServerError
from pyramid.renderers import JSON, render_to_response

from sqlalchemy.ext.associationproxy import _AssociationList

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'

log = logging.getLogger('pyramid_georest')


def get_mapping_from_request(request):
    if request.params is not None:
        return request.params.get('mapping')
    else:
        return None


class RenderProxy(object):

    def __init__(self):
        """
        A proxy which matches a renderer to a format which is passed in the url. It implements some basic
        renderers but is fully extend able. You can add renderers via the add renderer method.
        Please note that all renderers which are added to the proxy need to be added to the pyramid config
        before. Otherwise a error will be thrown on startup of the application.
        Please note in advance that the renderer system of pyramid works in a global way. It is your
        responsibility to ensure each renderer added is unique by its name. Please keep this in mind when
        some thing is not generating the output you want. Than it probably happens that you accidentally
        over wrote some renderer in another part of the application.

        See the following link for further information:
        http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html#adding-and-changing-renderers
        """
        self._format_to_renderer = {
            'json': 'geo_restful_json',
            'xml': 'geo_restful_xml',
            'geojson': 'geo_restful_geo_json'
        }

    def render(self, request, result, model_description):
        """
        Execute the rendering process by matching the requested format to the mapped renderer. If no
        renderer could be found a error is raised.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :param result: A list of database records found for the request.
        :type result: list of sqlalchemy.ext.declarative.DeclarativeMeta
        :param model_description: The description object of the data set which will be rendered.
        :type model_description: pyramid_georest.lib.description.ModelDescription
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        :raises: HTTPNotFound
        """
        response_format = request.matchdict['format']
        renderer_name = self._format_to_renderer.get(response_format, False)
        if renderer_name:
            return render_to_response(
                renderer_name,
                {
                    'features': result,
                    'model_description': model_description
                },
                request=request
            )
        else:
            text = 'The Format "{format}" is not defined for this service. Sorry...'.format(
                format=response_format
            )
            log.error(text)
            raise HTTPNotFound(
                detail=text
            )

    def add_renderer(self, delivery_format, renderer_name):
        """
        Adds a matching to the render proxy's matching dict. It is possible to overwrite an existing one.
        If you do, a notice (warning) is printed to your server logs.

        :param delivery_format: The format string to which the renderer should be bound to
            (e.g. "json", "xml", ...)
        :type delivery_format: str
        :param renderer_name: The name of the renderer which was used to assign it to the pyramid
            applications configuration.
        :type renderer_name: str
        :raises: ConfigurationError
        """
        if self._format_to_renderer.get(delivery_format):
            log.warning('You overwrite the renderer for the "{format_name}" format'.format(
                format_name=delivery_format)
            )
        self._format_to_renderer[delivery_format] = renderer_name


class AdapterProxy(object):

    def __init__(self):
        """
        A proxy which matches a client side adapter script to a adapter name which is passed in the url as
        format parameter. It implements some basic adapters but is fully extend able. You can add renderers
        via the "add_adapters" method.

        This enables you to provide every client side base implementation you like which is bound to a
        restful resource.
        """
        self._format_to_adapter = {}

    def render(self, request, model_description):
        """
        Execute the rendering process by matching the requested format to the mapped renderer. If no renderer
        could be found a error is raised.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :param model_description: The description object of the data set which will be rendered.
        :type model_description: pyramid_georest.lib.description.ModelDescription
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        :raises: HTTPNotFound
        """
        adapter_format = request.matchdict['format']
        adapter_renderer = self._format_to_adapter.get(adapter_format, False)
        if adapter_renderer:
            params = self.extend_return_params({})
            params['model_description'] = model_description
            return render_to_response(
                adapter_renderer,
                params,
                request=request
            )
        else:
            text = 'The Format "{format}" is not defined for this service. Sorry...'.format(
                format=adapter_renderer
            )
            log.error(text)
            raise HTTPNotFound(
                detail=text
            )

    @staticmethod
    def extend_return_params(params):
        """
        This method enables the developer to extend the parameter which are send to the template.
        :param params: The dictionary which holds the params.
        :type params: dict
        :return: The extended dictionary
        :rtype: dict
        """
        return params

    def add_adapter(self, delivery_format, adapter_renderer_path):
        """
        Adds a matching to the render proxy's matching dict. It is possible to overwrite an existing one.
        If you do, a notice (warning) is printed to your server logs.

        :param delivery_format: The format string to which the renderer should be bound to
            (e.g. "json", "xml", ...)
        :type delivery_format: str
        :param adapter_renderer_path: The name of the renderer which was used to assign it to the
            pyramid applications configuration.
        :type adapter_renderer_path: str
        :raises: ConfigurationError
        """
        if self._format_to_adapter.get(delivery_format):
            log.warning('You overwrite the renderer for the "{format_name}" format'.format(format_name=delivery_format))
        self._format_to_adapter[delivery_format] = adapter_renderer_path


class RestfulJson(JSON):
    """
    This represents an standard pyramid renderer which can consume a list of database instances and renders
    them to json. It is important to use the Base which is provided by this package. Because this class
    delivers additional methods.
    """

    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """

    def __call__(self, results, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request).
        :param results:
        :param system:
        :return:
        """

        request = system['request']
        # here the results will be serialized!!!!
        val = self.to_str(results)

        callback = request.GET.get('callback')
        if callback is None:
            ct = 'application/json'
            body = val
        else:
            ct = 'application/javascript'
            body = '%s(%s);' % (callback, val)
        response = request.response
        if response.content_type == response.default_content_type:
            response.content_type = ct
        return body

    def to_str(self, results):
        return simplejson.dumps(self.column_values_as_serializable(results))

    def column_values_as_serializable(self, results):
        serializable_results = []
        model_description = results.get('model_description', False)
        results = results.get('features', False)
        for result in results:
            result_dict = {}
            column_description = model_description.column_descriptions
            for column_name in column_description:
                value = getattr(result, column_name)
                if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
                    value = self.date_formatter(value)
                elif isinstance(value, _AssociationList):
                    value = self.association_formatter(value)
                elif isinstance(value, WKBElement):
                    value = self.geometry_formatter(value)
                elif isinstance(value, decimal.Decimal):
                    value = self.float_formatter(value)
                result_dict[column_name] = value
            serializable_results.append(result_dict)
        return serializable_results

    @staticmethod
    def date_formatter(date):
        """

        :param date: A date object which should be converted
        :type date: datetime.datetime
        :return: A string which represents the date object
        :rtype: str
        """
        return date.isoformat()

    @staticmethod
    def association_formatter(association):
        """

        :param association: A sqlalchemy association object which should be converted
        :type association: _AssociationList
        :return: A list containing the association
        :rtype: list of str
        """
        return list(association)

    def geometry_formatter(self, geometry):
        """

        :param geometry: A geoalchemy wkb element object which should be converted
        :type geometry: WKBElement
        :return: A WKT formatted string
        :rtype: str
        """
        return to_shape(geometry).wkt

    @staticmethod
    def float_formatter(number):
        """

        :param number: A floating point number be converted
        :type number: decimal.Decimal
        :return: The formatted float
        :rtype: float
        """
        return float(number)


class RestfulGeoJson(RestfulJson):
    """
        This represents an standard pyramid renderer which can consume a list of database instances and
        renders them to json. It is important to use the Base which is provided by this package. Because
        this class delivers additional methods.
        """

    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """
        super(RestfulGeoJson, self).__init__(info)

    def column_values_as_serializable(self, results):
        serializable_results = []
        model_description = results.get('model_description', False)
        results = results.get('features', False)
        for result in results:
            geometry = {}
            properties = {}
            result_dict = {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            }
            for column_name in model_description.column_descriptions:
                value = getattr(result, column_name)
                if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
                    value = self.date_formatter(value)
                elif isinstance(value, _AssociationList):
                    value = self.association_formatter(value)
                elif isinstance(value, WKBElement):
                    result_dict['geometry'] = self.geometry_formatter(value)
                    continue
                elif isinstance(value, decimal.Decimal):
                    value = self.float_formatter(value)
                properties[column_name] = value
            serializable_results.append(result_dict)
        return {
            "type": "FeatureCollection",
            "features": serializable_results
        }

    @staticmethod
    def geometry_type_formatter(geometry):
        """

        :param geometry: A geoalchemy wkb element object which should be converted
        :type geometry: WKBElement
        :return: A string representing a shapely valid geometry type
        :rtype: str
        """
        return to_shape(geometry).geom_type

    def geometry_formatter(self, geometry):
        """

        :param geometry: A geoalchemy wkb element object which should be converted
        :type geometry: WKBElement
        :return: A list of coordinates formatted string
        :rtype: list
        """
        shapely_object = to_shape(geometry)
        geom_type = shapely_object.geom_type
        if geom_type.upper() == 'POINT':
            return {
                "type": geom_type,
                "coordinates": list(shapely_object.coords[0])
            }
        elif geom_type.upper() == 'LINESTRING':
            return {
                "type": geom_type,
                "coordinates": list(shapely_object.coords)
            }
        elif geom_type.upper() == 'POLYGON':
            return {
                "type": geom_type,
                "coordinates": [list(shapely_object.exterior.coords)]
            }
        elif geom_type.upper() == 'MULTIPOINT':
            coordinates = list()
            for point in shapely_object.geoms:
                coordinates.append([list(point.coords[0])])
            return {
                "type": geom_type,
                "coordinates": coordinates
            }
        elif geom_type.upper() == 'MULTILINESTRING':
            coordinates = list()
            for point in shapely_object.geoms:
                coordinates.append([list(point.coords)])
            return {
                "type": geom_type,
                "coordinates": coordinates
            }
        elif geom_type.upper() == 'MULTIPOLYGON':
            coordinates = list()
            for polygon in shapely_object.geoms:
                coordinates.append([list(polygon.exterior.coords)])
            return {
                "type": geom_type,
                "coordinates": coordinates
            }
        elif geom_type.upper() == 'GEOMETRYCOLLECTION':
            members = []
            for inner_geometry in shapely_object.geoms:
                members.append(self.geometry_formatter(WKBElement(inner_geometry.wkb)))
            return {
                "type": geom_type,
                "members": members
            }
        else:
            raise HTTPServerError(
                'You try to access a Dataset with a "{type}" geometry type. This is not supported in the moment. '
                'Sorry...'.format(type=geom_type)
            )


class RestfulXML(RestfulJson):
    """
    This represents an standard pyramid renderer which can consume a list of database instances and renders
    them to xml. It is important to use the Base which is provided by this package. Because this class
    delivers additional methods.
    """

    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """
        super(RestfulXML, self).__init__(info)

    def __call__(self, results, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request). """

        request = system['request']

        # here the results will be serialized!!!!
        val = self.to_str(results)

        callback = request.GET.get('callback')
        if callback is None:
            ct = 'text/xml'
            body = val
        else:
            ct = 'text/xml'
            body = '%s(%s);' % (callback, val)
        response = request.response
        if response.content_type == response.default_content_type:
            response.content_type = ct
        return body

    def to_str(self, results):
        return dicttoxml.dicttoxml(self.column_values_as_serializable(results), attr_type=False)


class RestfulModelJSON(JSON):
    """
    This represents an standard pyramid renderer which can consume a list of database instances and renders
    them to xml. It is important to use the Base which is provided by this package. Because this class
    delivers additional methods.
    """

    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """

    def __call__(self, model_description, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request). """

        request = system['request']
        val = simplejson.dumps(model_description.as_dict())
        # print val
        callback = request.GET.get('callback')
        if callback is None:
            ct = 'application/json'
            body = val
        else:
            ct = 'application/javascript'
            body = '%s(%s);' % (callback, val)
        response = request.response
        if response.content_type == response.default_content_type:
            response.content_type = ct
        return body


class RestfulModelXML(JSON):
    """
    This represents an standard pyramid renderer which can consume a list of database instances and renders
    them to xml. It is important to use the Base which is provided by this package. Because this class
    delivers additional methods.
    """

    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """

    def __call__(self, model_description, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request). """

        request = system['request']
        dicttoxml.set_debug(False)
        val = dicttoxml.dicttoxml(model_description.as_dict(), attr_type=False)
        # print val
        callback = request.GET.get('callback')
        if callback is None:
            ct = 'text/xml'
            body = val
        else:
            ct = 'text/xml'
            body = '%s(%s);' % (callback, val)
        response = request.response
        if response.content_type == response.default_content_type:
            response.content_type = ct
        return body
