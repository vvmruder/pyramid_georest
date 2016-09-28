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


def doc(request):
    return {}


class RestProxy(object):
    read_method = 'GET'
    create_method = 'POST'
    update_method = 'PUT'
    delete_method = 'DELETE'

    def __init__(self, request):
        self.request = request
        api_name = request.matchdict['api_name']
        self.api = request.registry.pyramid_rest_apis.get(api_name)
        if self.api is None:
            raise HTTPNotFound(detail='API with name {name} is not defined.'.format(name=api_name))

    @view_config(
        route_name='read',
        request_method=read_method,
        permission=None  # 'read_json' if self.with_read_permission else None
    )
    def read(self):
        return self.api.read(self.request)

    @view_config(
        route_name='show',
        request_method=read_method,
        permission=None  # 'read_json' if self.with_read_permission else None
    )
    def show(self):
        return self.api.show(self.request)

    @view_config(
        route_name='create',
        request_method=create_method,
        permission=None  # 'read_json' if self.with_read_permission else None
    )
    def create(self):
        return self.api.create(self.request)

    @view_config(
        route_name='delete',
        request_method=delete_method,
        permission=None  # 'read_json' if self.with_read_permission else None
    )
    def delete(self):
        return self.api.delete(self.request)

    @view_config(
        route_name='update',
        request_method=update_method,
        permission=None  # 'read_json' if self.with_read_permission else None
    )
    def update(self):
        return self.api.update(self.request)

    @view_config(
        route_name='model',
        request_method=read_method,
        permission=None  # 'read_json' if self.with_read_permission else None
    )
    def model(self):
        return self.api.model(self.request)
