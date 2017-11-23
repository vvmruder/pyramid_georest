# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2016, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
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
from sqlalchemy import ColumnDefault
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import class_mapper
from yaml import load
from pyramid.path import AssetResolver

__author__ = 'Clemens Rudert'
__create_date__ = '21.09.16'


def translate(string_to_translate, dictionary, lang='de'):
    """
    A method which is able to translate a string with a given dictionary path on the file system. It acts in
    pyramid way.
    See:
    http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html?highlight=translation

    :param string_to_translate: The string which should be translated.
    :type string_to_translate: str
    :param dictionary: The dictionary which is used for translation.
    :type dictionary: str
    :param lang: The language to which the string should be translated.
    :type lang: str
    :return: The translated string
    :rtype: str
    """
    dictionary = load(open(AssetResolver().resolve(dictionary).abspath()))
    if string_to_translate in dictionary.get(lang):
        return dictionary.get(lang).get(string_to_translate)
    else:
        return string_to_translate


class RelationDescription(object):

    def __init__(self, relationship, name, dictionary=None):
        """
        A class to construct a description of a relationship property. It offers a method to get this description in a
        machine readable way. => as_dict

        :param relationship: The object which should be described
        :type relationship: sqlalchemy.orm.properties.RelationshipProperty
        :param name: The name of the element which should be described
        :type name: str
        :param dictionary: The pass to a dictionary. It has to be in the pyramid form:
         => http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html?highlight=translation
        :type dictionary: str or None
        """
        self.relationship = relationship

        self.column_name = name
        self.header = self.column_name if dictionary is None else translate(self.column_name, dictionary)
        # self.description = ModelDescription(self.relationship.argument)
        if self.relationship.uselist:
            # fk_path = [
            #     self.description.schema_name,
            #     self.description.table_name,
            #     ','.join(self.description.primary_key_column_names)
            # ]
            # self.foreign_key_names = [
            #     '.'.join(fk_path)
            # ]
            self.foreign_key_names = []
        else:
            self.foreign_key_names = []
        self.is_geometry_column = False
        self.type = 'String'
        self.is_primary_key = False
        self.has_foreign_keys = True
        self.length = None
        self.precision = None
        self.scale = None
        self.nullable = True
        self.default = []
        self.is_m_to_n = True
        self.connected_foreign_keys = []

        for foreign_key_column in self.relationship._calculated_foreign_keys:
            self.connected_foreign_keys.append(foreign_key_column.name)

    def as_dict(self):
        """
        Delivers the objects content as an dict.

        :return: An dictionary representing a description of the relationship in a application readable way
        :rtype: dict
        """
        return {
            'column_name': self.column_name,
            'header': self.header,
            'type': self.type,
            'is_primary_key': self.is_primary_key,
            'has_foreign_keys': self.has_foreign_keys,
            'foreign_key_names': self.foreign_key_names,
            'length': self.length,
            'precision': self.precision,
            'scale': self.scale,
            'nullable': self.nullable,
            'default': self.default,
            'is_m_to_n': self.is_m_to_n,
            'is_geometry_column': self.is_geometry_column,
            'connected_foreign_keys': self.connected_foreign_keys
        }


class ColumnDescription(object):

    def __init__(self, column, name, dictionary=None):
        """
        A class to construct a description of a column. It offers a method to get this description in a
        machine readable way. => as_dict

        :param column: The Column which should be the description for.
        :type column: sqlalchemy.schema.Column
        :param name: The column name
        :type name: str
        :param dictionary: The pass to a dictionary. It has to be in the pyramid form:
         => http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html?highlight=translation
        :type dictionary: str or None
        """
        self.column = column
        self.is_geometry_column = False
        self.srid = 0
        has_foreign_keys, foreign_key_names = self._column_fk()
        if 'geometry' in str(column.type):
            column_type = column.type.geometry_type
            self.is_geometry_column = True
            self.srid = column.type.srid
        else:
            column_type = column.type

        self.column_name = name
        self.header = self.column_name if dictionary is None else translate(self.column_name, dictionary)
        self.type = str(column_type)
        self.is_primary_key = column.primary_key
        self.has_foreign_keys = has_foreign_keys
        self.foreign_key_names = foreign_key_names
        self.length = self._column_length()
        self.precision = self._column_precision()
        self.scale = self._column_scale()
        self.nullable = column.nullable
        self.default = self._column_default()
        self.is_m_to_n = False

    def _column_fk(self):
        """
        Helper function, if column has foreign key relation.
        :return: Tuple of first: has foreign key relation or not (true/false) and corresponding a list of
            them or None
        :rtype : (bool, list) or (bool, None)
        """
        if self.column.foreign_keys:
            is_fk = True
            fks = []
            for key in self.column.foreign_keys:
                fks.append(str(key._get_colspec()))
        else:
            is_fk = False
            fks = None
        return is_fk, fks

    def _column_length(self):
        """
        Helper function, to obtain the lenght of the column which was provided (if type supports).
        :return: defined length for the passed column, None if so
        :rtype : int
        """
        if hasattr(self.column.type, "length"):
            length = self.column.type.length
        else:
            length = None
        return length

    def _column_precision(self):
        """
        Helper function, to obtain the precision of the column which was provided (if type supports).
        :return: defined precision for the passed column, None if so
        :rtype : int
        """
        if hasattr(self.column.type, "precision"):
            precision = self.column.type.precision
        else:
            precision = None
        return precision

    def _column_scale(self):
        """
        Helper function, to obtain the scale of the column which was provided (if type supports).
        :return: defined scale for the passed column, None if so
        :rtype : int
        """
        if hasattr(self.column.type, "scale"):
            scale = self.column.type.scale
        else:
            scale = None
        return scale

    def _column_default(self):
        """
        Helper function, to obtain the default value of the column which was provided (if type supports).
        :return: the value which was set as default for the passed column
        :rtype : int or str
        """
        if self.column.default is None:
            default = None
        elif type(self.column.default) is ColumnDefault:
            if hasattr(self.column.default.arg, '__call__'):
                default = None
            else:
                default = self.column.default.arg
        else:
            default = None
        return default

    def as_dict(self):
        """
        Delivers the objects content as an dict.

        :return: An dictionary representing a description of the column in a application readable way
        :rtype: dict
        """
        return {
            'column_name': self.column_name,
            'header': self.header,
            'type': self.type,
            'is_primary_key': self.is_primary_key,
            'has_foreign_keys': self.has_foreign_keys,
            'foreign_key_names': self.foreign_key_names,
            'length': self.length,
            'precision': self.precision,
            'scale': self.scale,
            'nullable': self.nullable,
            'default': self.default,
            'is_m_to_n': self.is_m_to_n,
            'is_geometry_column': self.is_geometry_column,
            'srid': self.srid
        }


class ModelDescription(object):

    def __init__(self, model, dictionary=None):
        """
        A class to construct a description of a sqlalchemy model. It offers a method to get this description in a
        machine readable way. => as_dict

        :param model: The sqlalchemy model which should be described.
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        :param dictionary: The pass to a dictionary. It has to be in the pyramid form:
         => http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html?highlight=translation
        :type dictionary: str
        """
        self.dictionary = dictionary
        self.model = model
        self.column_descriptions = {}
        self.column_classes = {}
        self.column_count = 0

        self.primary_key_columns = {}
        self.primary_key_column_names = []
        self.geometry_columns = {}
        self.geometry_column_names = []

        self.relationship_descriptions = {}
        self.relationship_count = 0
        self.relationship_classes = {}

        self.schema_name = self.model.__table__.schema
        self.table_name = self.model.__table__.name
        props = class_mapper(self.model)._props
        for name in props:
            value = props[name]
            if type(value) is not RelationshipProperty:
                if len(value.columns) != 1:
                    # print name, value.columns
                    # raise NotImplementedError
                    pass
                description = ColumnDescription(value.columns[0], name, dictionary=dictionary)
                self.column_descriptions[name] = description.as_dict()
                self.column_classes[name] = description.column
                if description.is_geometry_column:
                    self.geometry_columns[name] = description.column
                    self.geometry_column_names.append(name)
                if description.is_primary_key:
                    self.primary_key_columns[name] = description.column
                    self.primary_key_column_names.append(name)
                self.column_count += 1
            else:
                description = RelationDescription(value, name, dictionary=dictionary)
                self.relationship_descriptions[name] = description.as_dict()
                self.relationship_classes[name] = description.relationship
                self.relationship_count += 1

        self.primary_key_column_names = sorted(self.primary_key_column_names)

    def as_dict(self):
        """
        Delivers the objects content as an dict.

        :returns: An python dict with the description of the mapped database table
        :rtype : dict
        """
        return {
            'name': '',
            'primary_key_column_names': self.primary_key_column_names,
            'primary_key_column_count': len(self.primary_key_column_names),
            'geometry_column_names': self.geometry_column_names,
            'geometry_column_count': len(self.geometry_column_names),
            'relationship_count': self.relationship_count,
            'relationships': self.relationship_descriptions,
            'column_count': self.column_count,
            'columns': self.column_descriptions
        }
