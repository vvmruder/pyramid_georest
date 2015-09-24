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
__create_date__ = '27.10.2014'


def do_mapping(type_name, mapping=None):
    if mapping is not None:
        if mapping == 'extjs':
            type_name = TypeMapperEXT(type_name).type
        elif mapping == 'geoext':
            type_name = TypeMapperGeoEXT(type_name).type
    return type_name


class TypeMapper():
    __types__ = {
        'Boolean': [
            'BOOLEAN'
        ],
        'Date': [
            'DATE',
            'DATETIME',
            'TIMESTAMP',
            'TIME'
        ],
        'Float': [
            'NUMERIC',
            'DECIMAL',
            'NUMBER',
            'FLOAT',
            'REAL',
            'DOUBLE_PRECISION'
        ],
        'Integer': [
            'INTEGER',
            'INT',
            'BIGINT',
            'SMALLINT',
            'SERIAL',
            'BIGSERIAL'
        ],
        'String': [
            'UNICODE',
            'STRING',
            'CHAR',
            'NCHAR',
            'VARCHAR',
            'VARCHAR2',
            'NVARCHAR2',
            'TEXT',
            'LONG',
            'CLOB',
            'NCLOB'
        ]
    }

    def __init__(self, input_type):
        for map_type, test_types in self.__types__.iteritems():
            for tt in test_types:
                if input_type.upper() == tt:
                    self.type = map_type


class TypeMapperEXT(TypeMapper):
    __types__ = {
        'Boolean': [
            'BOOLEAN'
        ],
        'Float': [
            'NUMERIC',
            'DECIMAL',
            'NUMBER',
            'FLOAT',
            'REAL',
            'DOUBLE_PRECISION'
        ],
        'Integer': [
            'INTEGER',
            'INT',
            'BIGINT',
            'SMALLINT',
            'SERIAL',
            'BIGSERIAL'
        ],
        'String': [
            'UNICODE',
            'STRING',
            'CHAR',
            'NCHAR',
            'VARCHAR',
            'VARCHAR2',
            'NVARCHAR2',
            'TEXT',
            'LONG',
            'CLOB',
            'NCLOB'
        ],
        'Auto': [
            'GEOMETRY'
        ],
        'Date': [
            'DATE'
        ],
        'DateTime': [
            'DATETIME',
            'TIMESTAMP'
        ],
        'Time': [
            'TIME'
        ],
        'Point': [
            'POINT'
        ],
        'Polygon': [
            'POLYGON'
        ],
        'Linestring': [
            'LINESTRING'
        ],
        'Curve': [
            'CURVE'
        ],
        'Multipoint': [
            'MULTIPOINT'
        ],
        'Multilinestring': [
            'MULTILINESTRING'
        ],
        'Multipolygon': [
            'MULTIPOLYGON'
        ],
        'Geometrycollection': [
            'GEOMETRYCOLLECTION'
        ]
    }


class TypeMapperGeoEXT(TypeMapper):
    __types__ = {
        'Boolean': [
            'BOOLEAN'
        ],
        'Float': [
            'NUMERIC',
            'DECIMAL',
            'NUMBER',
            'FLOAT',
            'REAL',
            'DOUBLE_PRECISION'
        ],
        'Integer': [
            'INTEGER',
            'INT',
            'BIGINT',
            'SMALLINT',
            'SERIAL',
            'BIGSERIAL'
        ],
        'String': [
            'UNICODE',
            'STRING',
            'CHAR',
            'NCHAR',
            'VARCHAR',
            'VARCHAR2',
            'NVARCHAR2',
            'TEXT',
            'LONG',
            'CLOB',
            'NCLOB',
            'DATE',
            'DATETIME',
            'TIMESTAMP',
            'TIME'
        ],
        'Geometry':[
            'GEOMETRY'
        ],
        'Point': [
            'POINT'
        ],
        'Polygon': [
            'POLYGON'
        ],
        'Linestring': [
            'LINESTRING'
        ],
        'Curve': [
            'CURVE'
        ],
        'Multipoint': [
            'MULTIPOINT'
        ],
        'Multilinestring': [
            'MULTILINESTRING'
        ],
        'Multipolygon': [
            'MULTIPOLYGON'
        ],
        'Geometrycollection': [
            'GEOMETRYCOLLECTION'
        ]
    }