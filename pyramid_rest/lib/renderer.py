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
import decimal
import json
import datetime
import logging

import dicttoxml
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import JSON, render_to_response
from pyramid_rest.lib.description import ModelDescription

from pyramid_rest.lib.mapper import do_mapping
from sqlalchemy.ext.associationproxy import _AssociationList

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'

log = logging.getLogger('pyramid_rest')


def get_mapping_from_request(request):
    if request.params is not None:
        return request.params.get('mapping')
    else:
        return None


class RenderProxy(object):

    def __init__(self, request, result, model):
        self.request = request
        self.result = result
        self.model = model
        self.response_format = request.matchdict['format']

    def render(self):
        if self.response_format == 'json':
            return render_to_response(
                'restful_json',
                {
                    'features': self.result,
                    'model': self.model
                },
                request=self.request
            )
        elif self.response_format == 'xml':
            return render_to_response(
                'restful_xml',
                {
                    'features': self.result,
                    'model': self.model
                },
                request=self.request
            )
        elif self.response_format == 'geojson':
            return render_to_response(
                'restful_geo_json',
                {
                    'features': self.result,
                    'model': self.model
                },
                request=self.request
            )
        else:
            text = 'The Format "{format}" is not defined for this service. Sorry...'.format(
                format=self.response_format
            )
            log.error(text)
            raise HTTPNotFound(
                detail=text
            )


class RestfulJson(JSON):
    """
    This represents an standard pyramid renderer which can consume a list of database instances and renders them to
    json. It is important to use the Base which is provided by this package. Because this class delivers additional
    methods.
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
        (e.g. view, context, and request). """

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
        return json.dumps(self.column_values_as_serializable(results))

    def column_values_as_serializable(self, results):
        serializable_results = []
        model = results.get('model', False)
        model_description = ModelDescription(model)
        results = results.get('features', False)
        for result in results:
            result_dict = {}
            for column_name, column in model_description.column_descriptions.iteritems():
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

    @staticmethod
    def geometry_formatter(geometry):
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
        This represents an standard pyramid renderer which can consume a list of database instances and renders them to
        json. It is important to use the Base which is provided by this package. Because this class delivers additional
        methods.
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
        model = results.get('model', False)
        model_description = ModelDescription(model)
        results = results.get('features', False)
        for result in results:
            geometry = {}
            properties = {}
            result_dict = {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            }
            for column_name, column in model_description.column_descriptions.iteritems():
                value = getattr(result, column_name)
                if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
                    value = self.date_formatter(value)
                elif isinstance(value, _AssociationList):
                    value = self.association_formatter(value)
                elif isinstance(value, WKBElement):
                    geometry["coordinates"] = self.geometry_formatter(value)
                    geometry["type"] = self.geometry_type_formatter(value)
                    continue
                elif isinstance(value, decimal.Decimal):
                    value = self.float_formatter(value)
                properties[column_name] = value
            serializable_results.append(result_dict)
        return serializable_results

    @staticmethod
    def geometry_type_formatter(geometry):
        """

        :param geometry: A geoalchemy wkb element object which should be converted
        :type geometry: WKBElement
        :return: A string representing a shapely valid geometry type
        :rtype: str
        """
        return to_shape(geometry).geom_type

    @staticmethod
    def geometry_formatter(geometry):
        """

        :param geometry: A geoalchemy wkb element object which should be converted
        :type geometry: WKBElement
        :return: A list of coordinates formatted string
        :rtype: list
        """
        shapely_object = to_shape(geometry)
        geom_type = shapely_object.geom_type
        if geom_type == 'Point':
            coordinates = list(shapely_object.coords)
        else:
            coordinates = list(shapely_object.exterior.coords)
        return coordinates


class RestfulXML(RestfulJson):
    """
    This represents an standard pyramid renderer which can consume a list of database instances and renders them to
    xml. It is important to use the Base which is provided by this package. Because this class delivers additional
    methods.
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
    This represents an standard pyramid renderer which can consume a list of database instances and renders them to
    xml. It is important to use the Base which is provided by this package. Because this class delivers additional
    methods.
    """

    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """

    def __call__(self, objects, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request). """

        request = system['request']
        columns = objects.get('columns')
        for column in columns:
            column['type'] = do_mapping(column.get('type'), get_mapping_from_request(request))
        objects['columns'] = columns
        val = json.dumps(objects)
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
    This represents an standard pyramid renderer which can consume a list of database instances and renders them to
    xml. It is important to use the Base which is provided by this package. Because this class delivers additional
    methods.
    """

    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """

    def __call__(self, objects, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request). """

        request = system['request']
        dicttoxml.set_debug(False)
        columns = objects.get('columns')
        for column in columns:
            column['type'] = do_mapping(column.get('type'), get_mapping_from_request(request))
        objects['columns'] = columns
        val = dicttoxml.dicttoxml(objects, attr_type=False)
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
