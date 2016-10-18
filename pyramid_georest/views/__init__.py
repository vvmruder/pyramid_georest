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
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'


class RestProxy(object):

    def __init__(self, request):
        """
        A view configuration represented by a class. This is the central entry point of the api. Each request to every
        api/service comes through this point. At this point we decide which api was called and which action was
        requested (read/show/create/update/delete/model).

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :raises: HTTPNotFound
        """
        self.request = request
        api_name = request.matchdict['api_name']
        self.api = request.registry.pyramid_georest_apis.get(api_name)
        if self.api is None:
            raise HTTPNotFound(detail='API with name {name} is not defined.'.format(name=api_name))

    def read(self):
        """
        Simple pass through method. We only need it to have a central entry to the

        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.api.read(self.request)

    def show(self):
        """
        Simple pass through method.

        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.api.show(self.request)

    def create(self):
        """
        Simple pass through method.

        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.api.create(self.request)

    def delete(self):
        """
        Simple pass through method.

        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.api.delete(self.request)

    def update(self):
        """
        Simple pass through method.

        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.api.update(self.request)

    def model(self):
        """
        Simple pass through method.

        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.api.model(self.request)
