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


__author__ = 'Clemens Rudert'


def includeme(config):
    # delivers multiple records
    config.add_route('read', '/{api_name}/{schema_name}/{table_name}/read/{format}')
    # delivers specific record
    config.add_route('show', '/{api_name}/{schema_name}/{table_name}/read/{format}*primary_keys')
    # create specific record
    config.add_route('create', '/{api_name}/{schema_name}/{table_name}/create/{format}')
    # update specific record
    config.add_route('update', '/{api_name}/{schema_name}/{table_name}/update/{format}*primary_keys')
    # delete specific record
    config.add_route('delete', '/{api_name}/{schema_name}/{table_name}/delete/{format}*primary_keys')
    # delivers the description of the desired dataset
    config.add_route('model', '/{api_name}/{schema_name}/{table_name}/model/{format}')
