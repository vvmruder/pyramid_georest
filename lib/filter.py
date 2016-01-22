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
__create_date__ = '09.09.2015'


from geoalchemy2.elements import WKTElement
from sqlalchemy.sql.expression import text
from sqlalchemy import or_, and_
from sqlalchemy import cast
from sqlalchemy import String


class Filter():

    def __init__(self, filter_definition, mapped_class, db_session):
        """

        :param filter_definition:
        :param mapped_class:
        """
        self.filter_list = list()
        self.filter_list_and = list()
        self.filter_list_or = list()
        self.mapped_class = mapped_class
        self.db_session = db_session
        self.query = db_session.query(mapped_class)
        self.mode = filter_definition.get('mode')
        self.filters = [] if filter_definition.get('filters') is None else filter_definition.get('filters')
        self.limit = filter_definition.get('limit')
        self.order_by = filter_definition.get('order_by')
        self.offset = filter_definition.get('offset')

    def __str__(self):
        return 'Mode=' + self.mode + ', Filters=' + str(self.filters)

    def do_filter(self):
        """


        :return:
        """

        for f in self.filters:
            self.__decide_filter__(f)
        if self.mode == 'AND':
            self.query = self.query.filter(and_(*self.filter_list))
        elif self.mode == 'OR':
            self.query = self.query.filter(or_(*self.filter_list))
        elif self.mode == 'NONE':
            for f in self.filter_list:
                self.query = self.query.filter(~f)
        else:
            pass
        self.query = self.query.filter(or_(*self.filter_list_or))
        self.query = self.query.filter(and_(*self.filter_list_and))
        if self.limit is not None:
            self.query = self.query.order_by(self.mapped_class.__pk__())
            self.query = self.query.limit(self.limit)
        else:
            pass
        self.query.with_labels()
        # print self.query.statement
        return self.query

    def __decide_filter__(self, filter):
        """

        :param filter:
        """
        operator = filter.get('operator')
        column_name = filter.get('column')
        value = filter.get('value')
        if isinstance(value, basestring):
            value = value.encode('utf-8')
        for col in self.mapped_class.__table__.columns:
            if col.name == column_name:
                if operator == '=':
                    self.filter_list.append(col == value)
                elif operator == '<>':
                    self.filter_list.append(col != value)
                elif operator == '<':
                    self.filter_list.append(col < value)
                elif operator == '<=':
                    self.filter_list.append(col <= value)
                elif operator == '>':
                    self.filter_list.append(col > value)
                elif operator == '>=':
                    self.filter_list.append(col >= value)
                elif operator == 'LIKE':
                    self.filter_list.append((cast(col, String(length=100)).like(str(value))))
                elif operator == 'IN':
                    self.filter_list.append(col.in_(str(value).split(',')))
                elif operator == 'NULL':
                    self.filter_list.append(col == None)
                elif operator == 'NOT_NULL':
                    self.filter_list.append(col != None)
                elif operator == 'INTERSECTS':
                    self.decide_geometric_relation_type(value, column_name, 'ST_Intersects')
                elif operator == 'TOUCHES':
                    self.decide_geometric_relation_type(value, column_name, 'ST_Touches')
                elif operator == 'COVERED_BY':
                    self.decide_geometric_relation_type(value, column_name, 'ST_Covers')
                elif operator == 'WITHIN':
                    self.decide_geometric_relation_type(value, column_name, 'ST_Within')

    def decide_geometric_relation_type(self, value, column_name, compare_type):
        columns = self.mapped_class.description().get('columns')
        for column in columns:
            if column.get('column_name') == column_name:
                if 'GEOMETRYCOLLECTION' in column.get('type'):
                    self.extract_geometry_collection_db(value, compare_type, column_name)
                elif 'GEOMETRYCOLLECTION' in value:
                    self.extract_geometry_collection_input(value, compare_type, column_name)
                elif 'GEOMETRYCOLLECTION' in value and column.get('type') == 'GEOMETRYCOLLECTION':
                    self.extract_geometry_collection_input_and_db(value, compare_type, column_name)
                elif column.get('type') != 'GEOMETRYCOLLECTION':
                    if compare_type == 'ST_Intersects':
                        self.filter_list.append(getattr(self.mapped_class, column_name).intersects(WKTElement(value, srid=2056)))
                    elif compare_type == 'ST_Touches':
                        self.filter_list.append(getattr(self.mapped_class, column_name).touches(WKTElement(value, srid=2056)))
                    elif compare_type == 'ST_Covers':
                        self.filter_list.append(getattr(self.mapped_class, column_name).covered_by(WKTElement(value, srid=2056)))
                    elif compare_type == 'ST_Within':
                        self.filter_list.append(getattr(self.mapped_class, column_name).within(WKTElement(value, srid=2056)))

    def extract_geometry_collection_db(self, compare_geometry, compare_type, column_name):
        db_path_list = [
            self.mapped_class.__table_args__.get('schema'),
            self.mapped_class.__table__.name,
            column_name
        ]
        db_path = '.'.join(db_path_list)
        sql_text_point = '{0}(ST_CollectionExtract({1}, 1), ST_GeomFromText(\'{2}\', 2056))'.format(compare_type, db_path, compare_geometry)
        sql_text_line = '{0}(ST_CollectionExtract({1}, 2), ST_GeomFromText(\'{2}\', 2056))'.format(compare_type, db_path, compare_geometry)
        sql_text_polygon = '{0}(ST_CollectionExtract({1}, 3), ST_GeomFromText(\'{2}\', 2056))'.format(compare_type, db_path, compare_geometry)
        self.filter_list_or.append(text(sql_text_point))
        self.filter_list_or.append(text(sql_text_line))
        self.filter_list_or.append(text(sql_text_polygon))

    def extract_geometry_collection_input(self, compare_geometry, compare_type, column_name):
        db_path_list = [
            self.mapped_class.__table_args__.get('schema'),
            self.mapped_class.__table__.name,
            column_name
        ]
        db_path = '.'.join(db_path_list)
        sql_text_point = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 1))'.format(compare_type, db_path, compare_geometry)
        sql_text_line = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 2))'.format(compare_type, db_path, compare_geometry)
        sql_text_polygon = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 3))'.format(compare_type, db_path, compare_geometry)
        self.filter_list_or.append(text(sql_text_point))
        self.filter_list_or.append(text(sql_text_line))
        self.filter_list_or.append(text(sql_text_polygon))

    def extract_geometry_collection_input_and_db(self, compare_geometry, compare_type, column_name):
        db_path_list = [
            self.mapped_class.__table_args__.get('schema'),
            self.mapped_class.__table__.name,
            column_name
        ]
        db_path = '.'.join(db_path_list)
        sql_text_point = '{0}((ST_CollectionExtract({1}, 1), ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 1))'.format(compare_type, db_path, compare_geometry)
        sql_text_line = '{0}((ST_CollectionExtract({1}, 2), ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 2))'.format(compare_type, db_path, compare_geometry)
        sql_text_polygon = '{0}((ST_CollectionExtract({1}, 3), ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 3))'.format(compare_type, db_path, compare_geometry)
        self.filter_list_or.append(text(sql_text_point))
        self.filter_list_or.append(text(sql_text_line))
        self.filter_list_or.append(text(sql_text_polygon))