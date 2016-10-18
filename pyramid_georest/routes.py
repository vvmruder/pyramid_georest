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
from pyramid_georest.views import RestProxy

__author__ = 'Clemens Rudert'

read_method = 'GET'
read_filter_method = 'POST'
create_method = 'POST'
update_method = 'PUT'
delete_method = 'DELETE'


def includeme(config):
    global read_method, read_filter_method, create_method, update_method, delete_method
    from pyramid_georest import CREATE, UPDATE, DELETE, READ, READ_FILTER

    # set methods from ini configuration if set. Use standard if not.
    if CREATE is not None:
        create_method = CREATE
    if UPDATE is not None:
        update_method = UPDATE
    if DELETE is not None:
        delete_method = DELETE
    if READ is not None:
        read_method = READ
    if READ_FILTER is not None:
        read_filter_method = READ_FILTER

    # delivers multiple records
    config.add_route('read', '/{api_name}/{schema_name}/{table_name}/read/{format}')
    config.add_view(RestProxy, route_name='read', attr='read', request_method=(read_method, read_filter_method))

    # delivers specific record
    config.add_route('show', '/{api_name}/{schema_name}/{table_name}/read/{format}*primary_keys')
    config.add_view(RestProxy, route_name='show', attr='show', request_method=read_method)

    # create specific record
    config.add_route('create', '/{api_name}/{schema_name}/{table_name}/create/{format}')
    config.add_view(RestProxy, route_name='create', attr='create', request_method=create_method)

    # update specific record
    config.add_route('update', '/{api_name}/{schema_name}/{table_name}/update/{format}*primary_keys')
    config.add_view(RestProxy, route_name='update', attr='update', request_method=update_method)

    # delete specific record
    config.add_route('delete', '/{api_name}/{schema_name}/{table_name}/delete/{format}*primary_keys')
    config.add_view(RestProxy, route_name='delete', attr='delete', request_method=delete_method)

    # delivers the description of the desired dataset
    config.add_route('model', '/{api_name}/{schema_name}/{table_name}/model/{format}')
    config.add_view(RestProxy, route_name='model', attr='model', request_method=read_method)
