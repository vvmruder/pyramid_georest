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
import json
from pyramid.renderers import JSON
import dicttoxml

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'


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

    def __call__(self, objects, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request). """

        request = system['request']
        features = []
        for o in objects.get('features'):
            features.append(o.as_dict())
        val = json.dumps(features)
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


class RestfulXML(JSON):
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
        features = []
        for o in objects.get('features'):
            features.append(o.as_dict())
        dicttoxml.set_debug(False)
        val = dicttoxml.dicttoxml(features, attr_type=False)
        print val
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
        val = dicttoxml.dicttoxml(objects, attr_type=False)
        print val
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