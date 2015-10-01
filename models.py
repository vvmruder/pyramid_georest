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
import datetime
import decimal
from pyramid.path import AssetResolver
from sqlalchemy.ext.associationproxy import _AssociationList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import ColumnCollection
from sqlalchemy.orm import class_mapper, RelationshipProperty
from sqlalchemy import Column, types, ColumnDefault, PrimaryKeyConstraint, Sequence
from geoalchemy import GeometryColumn, Polygon, GeometryDDL, PersistentSpatialElement
from shapely.wkb import loads as loadsWKB
from yaml import load

__author__ = 'Clemens Rudert'
__create_date__ = '23.07.2015'


class RestfulBase(object):

    @classmethod
    def translate(cls, string_to_translate, dictionary, lang='de'):
        dictionary = load(open(AssetResolver().resolve(dictionary).abspath()))
        if string_to_translate in dictionary.get(lang):
            return dictionary.get(lang).get(string_to_translate)
        else:
            return string_to_translate

    @classmethod
    def description(cls, dictionary=None):
        """
        :returns: An python dict with the description of the mapped database table
        :rtype : dict
        """


        primary_keys = []
        model = {
            'model_name': cls.__name__,
            'columns': [],
            'relations': []
        }
        for name, value in class_mapper(cls)._props.iteritems():

            if type(value) is not RelationshipProperty:
                if len(value.columns) != 1:
                    # print name, value.columns
                    # raise NotImplementedError
                    pass
                column = value.columns[0]
                fk, fks = cls.column_fk(column)
                column_dict = {
                    'column_name': name,
                    'header': name if dictionary is None else cls.translate(name, dictionary),
                    'type': str(column.type.__visit_name__ if column.type.__visit_name__ != 'user_defined' else column.type),
                    'pk': column.primary_key,
                    'fk': fk,
                    'fk_names': fks,
                    'length': cls.column_length(column),
                    'precision': cls.column_precision(column),
                    'scale': cls.column_scale(column),
                    'nullable': column.nullable,
                    'default': cls.column_default(column),
                    'is_m_to_n': False
                }
                model.get('columns').append(column_dict)
                if column.primary_key:
                    primary_keys.append(name)
                if len(primary_keys) == 1:
                    model['pk_name'] = primary_keys[0]
                elif len(primary_keys) > 1:
                    model['pk_names'] = primary_keys
            else:
                # TODO: make relationship properties part of the model description. This can be helpful for dropdowns
                #  etc.
                if value.uselist:
                    fk_path = [
                        value.argument.__table_args__.get('schema'),
                        value.argument.__table__.name,
                        value.argument.description().get('pk_name')
                    ]
                    column_dict = {
                        'column_name': name,
                        'type': 'String',
                        'pk': False,
                        'fk': True,
                        'fk_names': [
                            '.'.join(fk_path)
                        ],
                        'length': None,
                        'precision': None,
                        'scale': None,
                        'nullable': True,
                        'default': [],
                        'is_m_to_n': True
                    }
                    model.get('columns').append(column_dict)
        model['columns_count'] = len(model.get('columns'))
        return model

    @staticmethod
    def column_fk(column):
        """
        Helper function, if column has foreign key relation.


        :param column: A SQLAlchemy column object
        :type column: Column
        :return: Tuple of first: has foreign key relation or not (true/false) and corresponding a list of them or None
        :rtype : (bool, list) or (bool, None)
        """
        if column.foreign_keys:
            is_fk = True
            fks = []
            for key in column.foreign_keys:
                fks.append(str(key._get_colspec()))
        else:
            is_fk = False
            fks = None
        return is_fk, fks

    @staticmethod
    def column_length(column):
        """
        Helper function, to obtain the lenght of the column which was provided (if type supports).


        :param column: A SQLAlchemy column object
        :type column: Column
        :return: defined length for the passed column, None if so
        :rtype : int
        """
        if hasattr(column.type, "length"):
            length = column.type.length
        else:
            length = None
        return length

    @staticmethod
    def column_precision(column):
        """
        Helper function, to obtain the precision of the column which was provided (if type supports).


        :param column: A SQLAlchemy column object
        :type column: Column
        :return: defined precision for the passed column, None if so
        :rtype : int
        """
        if hasattr(column.type, "precision"):
            precision = column.type.precision
        else:
            precision = None
        return precision

    @staticmethod
    def column_scale(column):
        """
        Helper function, to obtain the scale of the column which was provided (if type supports).


        :param column: A SQLAlchemy column object
        :type column: Column
        :return: defined scale for the passed column, None if so
        :rtype : int
        """
        if hasattr(column.type, "scale"):
            scale = column.type.scale
        else:
            scale = None
        return scale

    @staticmethod
    def column_default(column):
        """
        Helper function, to obtain the default value of the column which was provided (if type supports).


        :param column: A SQLAlchemy column object
        :type column: Column
        :return: the value which was set as default for the passed column
        :rtype : int or str
        """
        if column.default is None:
            default = None
        elif type(column.default) is ColumnDefault:
            if hasattr(column.default.arg, '__call__'):
                default = column.default.is_callable
            else:
                default = column.default.arg
        else:
            default = None
        return default

    @classmethod
    def database_path(cls):
        table_name = cls.__table__.name
        schema = cls.__table__.schema
        if schema is not None:
            path = '{0}.{1}'.format(schema, table_name)
        else:
            path = table_name
        return path

    def as_dict(self):
        """

        Helper function, to obtain the values of the database object in a python consumable format

        :rtype : dict
        :return: a dict representing the key value pairs of corresponding database entity
        """
        result = {}
        for column in self.description().get('columns', []):
            name = column.get('column_name')
            is_m_to_n = column.get('is_m_to_n')
            value = getattr(self, name)
            if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
                value = value.isoformat()
            elif isinstance(value, _AssociationList):
                value = list(value)
            elif isinstance(value, PersistentSpatialElement):
                value = loadsWKB(str(value.geom_wkb)).wkt
            elif isinstance(value, decimal.Decimal):
                value = float(value)
            elif is_m_to_n:
                value_list = []
                for value_list_element in value:
                    pk_name = value_list_element.description().get('pk_name')
                    pk_value = getattr(value_list_element, pk_name)
                    value_list.append(str(pk_value))
                value = ','.join(value_list)
            result[name] = value
        return result

    @classmethod
    def pk_columns(cls):
        """

        Helper function, to obtain the Column objects which are bound to an PrimaryKeyConstraint in the corresponding
        mapper.

        :rtype : ColumnCollection
        :return: a ColumnCollection containing all primary key related Column objects
        """
        return cls.__table__.primary_key.columns

    @classmethod
    def pk_column_names(cls):
        return cls.__table__.primary_key.columns.keys()

Base = declarative_base(cls=RestfulBase)