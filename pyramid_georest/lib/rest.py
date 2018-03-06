# -*- coding: utf-8 -*-

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
from __future__ import print_function
import logging
import transaction
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.request import Request
from pyramid_georest.lib.description import ModelDescription
from pyramid_georest.lib.renderer import RenderProxy, AdapterProxy
from pyramid_georest.lib.database import Connection
from pyramid_georest.routes import create_api_routing, check_route_prefix
from sqlalchemy import or_, and_, cast, String, desc, asc
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound
from geoalchemy2 import WKTElement
from shapely.geometry import asShape

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'

log = logging.getLogger('pyramid_georest')

DIRECTION_ASC = ['ASC', 'asc', 'ascending']
DIRECTION_DESC = ['DESC', 'desc', 'descending']


class Clause(object):

    def __init__(self, definition, model_description):
        """
        The class which represents the clause block.

        Args:
            definition (dict): The values which are assigned to the object.
            model_description (pyramid_georest.lib.description.ModelDescription): The description of the model
                which is being filtered.
        Raises:
            HTTPBadRequest
        """

        self.model_description = model_description

        if definition.get('column_name'):
            self.column_name = definition.get('column_name')
            self.column = model_description.column_classes.get(self.column_name)
            self.column_description = model_description.column_descriptions.get(self.column_name)
        else:
            raise HTTPBadRequest(
                'Passed clause block does not contain the column_name. Definition was: {}'.format(definition)
            )

        if definition.get('operator'):
            self.operator = definition.get('operator')
        else:
            raise HTTPBadRequest(
                'Passed clause block does not contain the operator. Definition was: {}'.format(definition)
            )

        self.value = definition.get('value')

        if self.column_description.get('is_geometry_column'):
            self.clause_construct = self.decide_multi_geometries()
        else:
            self.clause_construct = self.decide_operator()

    def decide_operator(self):
        """
        This method is used by the filter object to make a simple matching between the passed operators and
        the operators which are useable for filtering against the database.
        There are only some base operators implemented by default. If you like some more specific ones feel
        free to subclass this class and overwrite this method with your special behaviour and matching.
        Note that this method does not only do the matching thing. It constructs the whole binary expression.
        So you can get some influence on this process too.

        Returns:
            sqlalchemy.sql.expression._BinaryExpression: The clause element
        Raises:
            HTTPBadRequest
        """
        if self.operator == '=':
            clause = self.column == self.value
        elif self.operator == '==':
            clause = self.column == self.value
        elif self.operator == '<>':
            clause = self.column != self.value
        elif self.operator == '!=':
            clause = self.column != self.value
        elif self.operator == '<':
            clause = self.column < self.value
        elif self.operator == '<=':
            clause = self.column <= self.value
        elif self.operator == '>':
            clause = self.column > self.value
        elif self.operator == '>=':
            clause = self.column >= self.value
        elif self.operator == 'LIKE':
            clause = cast(self.column, String()).like(self.value)
        elif self.operator == 'IN':
            clause = self.column.in_(str(self.value).split(','))
        elif self.operator == 'NULL':
            clause = self.column == None
        elif self.operator == 'NOT_NULL':
            clause = self.column != None
        else:
            raise HTTPBadRequest('The operator "{operator}" you passed is not implemented.'.format(
                operator=self.operator)
            )
        return clause

    @staticmethod
    def decide_geometric_operator_(operator):
        """
        Maps the passed operator to the correct database method operator
        Args:
            operator (str): The Operator from api request.
        Returns:
            str
        """
        if operator == 'INTERSECTS':
            operator = 'ST_Intersects'
        elif operator == 'TOUCHES':
            operator = 'ST_Touches'
        elif operator == 'COVERED_BY':
            operator = 'ST_CoveredBy'
        elif operator == 'WITHIN':
            operator = 'ST_DFullyWithin'
        else:
            raise HTTPBadRequest('The operator "{operator}" you passed is not implemented.'.format(
                operator=operator
            ))
        return operator

    def decide_multi_geometries(self):
        """
        This method decides if the clause will contain geometry collections (in the value or in the
        database or in both).
        If it does it is necessary to "unpack" all collections to make them valid for geometric operations
        in database.
        If it does not it uses a normal geometric operation.

        Returns:
            sqlalchemy.sql.expression._BinaryExpression: The clause element

        Raises:
            HTTPBadRequest
        """
        geometry_type = str(self.column_description.get('type')).upper()
        db_path_list = [
            self.model_description.schema_name,
            self.model_description.table_name,
            self.column_description.get('column_name')
        ]
        db_path = '.'.join(db_path_list)
        srid = self.column_description.get('srid')
        if geometry_type == 'GEOMETRYCOLLECTION' and 'GEOMETRYCOLLECTION' not in self.value:
            clause_construct = self.extract_geometry_collection_db(db_path, srid)
        elif 'GEOMETRYCOLLECTION' in self.value and geometry_type != 'GEOMETRYCOLLECTION':
            clause_construct = self.extract_geometry_collection_input(db_path, srid)
        elif 'GEOMETRYCOLLECTION' in self.value and geometry_type == 'GEOMETRYCOLLECTION':
            clause_construct = self.extract_geometry_collection_input_and_db(db_path, srid)
        elif geometry_type != 'GEOMETRYCOLLECTION' and 'GEOMETRYCOLLECTION' not in self.value:
            clause_construct = self.decide_geometric_operation(srid)
        else:
            hint_text = "You found some bad geometric circumstance. Sorry for that. We can't handle your " \
                        "request uses the operation {operation} on a geometric column with the type " \
                        "{geometry_type} and your passed geometry was of the value {value}. This is not " \
                        "supported in the moment.".format(
                            operation=self.operator,
                            geometry_type=geometry_type,
                            value=self.value
                        )
            raise HTTPBadRequest(hint_text)
        return clause_construct

    def decide_geometric_operation(self, srid):
        """
        Decides the simple cases of geometric filter operations.

        Args:
            srid (int): The SRID/EPSG number to define the coordinate system of the geometry attribute.

        Returns:
            sqlalchemy.sql.expression._BinaryExpression: The clause element

        Raises:
            HTTPBadRequest
        """
        if self.operator == 'INTERSECTS':
            clause = self.column.ST_Intersects(WKTElement(self.value, srid=srid))
        elif self.operator == 'TOUCHES':
            clause = self.column.ST_Touches(WKTElement(self.value, srid=srid))
        elif self.operator == 'COVERED_BY':
            clause = self.column.ST_CoveredBy(WKTElement(self.value, srid=srid))
        elif self.operator == 'WITHIN':
            clause = self.column.ST_DFullyWithin(WKTElement(self.value, srid=srid))
        else:
            raise HTTPBadRequest('The operator "{operator}" you passed is not implemented.'.format(
                operator=self.operator)
            )
        return clause

    def extract_geometry_collection_db(self, db_path, srid):
        """
        Decides the geometry collections cases of geometric filter operations when the database contains multi
        geometries but the passed geometry does not.
        The multi geometry will be extracted to it's sub parts for operation.

        Args:
            srid (int): The SRID/EPSG number to define the coordinate system of the geometry attribute.
            db_path (str): The point separated string of schema_name.table_name.column_name from which we can
                construct a correct SQL statement.

        Returns:
            sqlalchemy.sql.elements.BooleanClauseList: The clause element.

        Raises:
            HTTPBadRequest
        """
        operator = self.decide_geometric_operator_(self.operator)
        sql_text_point = '{0}(ST_CollectionExtract({1}, 1), ST_GeomFromText(\'{2}\', {3}))'.format(
            operator,
            db_path,
            self.value,
            srid
        )
        sql_text_line = '{0}(ST_CollectionExtract({1}, 2), ST_GeomFromText(\'{2}\', {3}))'.format(
            operator,
            db_path,
            self.value,
            srid
        )
        sql_text_polygon = '{0}(ST_CollectionExtract({1}, 3), ST_GeomFromText(\'{2}\', {3}))'.format(
            operator,
            db_path,
            self.value,
            srid
        )
        clause_blocks = [
            text(sql_text_point),
            text(sql_text_line),
            text(sql_text_polygon)
        ]
        return or_(*clause_blocks)

    def extract_geometry_collection_input(self, db_path, srid):
        """
        Decides the geometry collections cases of geometric filter operations when the database
        contains multi geometries but the passed geometry does not.
        The multi geometry will be extracted to it's sub parts for operation.

         Args:
            srid (int): The SRID/EPSG number to define the coordinate system of the geometry attribute.
            db_path (str): The point separated string of schema_name.table_name.column_name from which we can
                construct a correct SQL statement.

        Returns:
            sqlalchemy.sql.elements.BooleanClauseList: The clause element.

        Raises:
            HTTPBadRequest
        """
        operator = self.decide_geometric_operator_(self.operator)
        sql_text_point = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', {3}), 1))'.format(
            operator,
            db_path,
            self.value,
            srid
        )
        sql_text_line = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', {3}), 2))'.format(
            operator,
            db_path,
            self.value,
            srid
        )
        sql_text_polygon = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', {3}), 3))'.format(
            operator,
            db_path,
            self.value,
            srid
        )
        clause_blocks = [
            text(sql_text_point),
            text(sql_text_line),
            text(sql_text_polygon)
        ]
        return or_(*clause_blocks)

    def extract_geometry_collection_input_and_db(self, db_path, srid):
        """
        Decides the geometry collections cases of geometric filter operations when the database
        contains multi geometries but the passed geometry does not.
        The multi geometry will be extracted to it's sub parts for operation.

         Args:
            srid (int): The SRID/EPSG number to define the coordinate system of the geometry attribute.
            db_path (str): The point separated string of schema_name.table_name.column_name from which we can
                construct a correct SQL statement.

        Returns:
            sqlalchemy.sql.elements.BooleanClauseList: The clause element.

        Raises:
            HTTPBadRequest
        """
        operator = self.decide_geometric_operator_(self.operator)
        sql_text_point = '{0}(ST_CollectionExtract({1}, 1), ST_CollectionExtract(' \
                         'ST_GeomFromText(\'{2}\', {3}), 1))'.format(operator, db_path, self.value, srid)
        sql_text_line = '{0}(ST_CollectionExtract({1}, 2), ST_CollectionExtract(' \
                        'ST_GeomFromText(\'{2}\', {3}), 2))'.format(operator, db_path, self.value, srid)
        sql_text_polygon = '{0}(ST_CollectionExtract({1}, 3), ST_CollectionExtract(' \
                           'ST_GeomFromText(\'{2}\', {3}), 3))'.format(operator, db_path, self.value, srid)
        clause_blocks = [
            text(sql_text_point),
            text(sql_text_line),
            text(sql_text_polygon)
        ]
        return or_(*clause_blocks)


class FilterBlock(object):

    def __init__(self, model_description, definition=None):
        """
        The class which represents the filter block.

        Args:
            definition (dict): The values which are assigned to the object. The definition of the Filter.
                It has to be dict like {"mode": "OR/AND", "clauses": []}.
                The clauses are also dict objects with the pattern:
                    {
                        "column_name": "<name>",
                        "operator": "<see static method decide_operator for further detail>",
                        "value":<value>
                    }
                It is possible to pack a definition of filter inside the clause array.
                This enables complex queries.
            model_description (pyramid_georest.lib.description.ModelDescription): The description of the model
                which is being filtered.
        """

        if definition is None:
            definition = {}

        self.model_description = model_description

        self.mode = 'AND'

        if definition.get('mode'):
            self.mode = definition.get('mode')
        else:
            log.info('Initialize empty filter block with mode AND')

        self.clauses = []
        if definition.get('clauses'):
            for clause_definition in definition.get('clauses'):
                self.add_clause(clause_definition)
        else:
            log.info('Initialize filter block with empty clauses')

        self.clause = self.decide_mode()

    def add_clause(self, clause_definition):
        """
        The class which represents the clause block.

        Args:
            clause_definition (dict): The values which are assigned to the object.
        """
        if clause_definition.get('mode'):
            self.clauses.append(FilterBlock(self.model_description, clause_definition).clause)
        else:
            self.clauses.append(Clause(clause_definition, self.model_description).clause_construct)

    def decide_mode(self):
        """
        This method is used to match the mode and construct a clause list in which are each single
        filter clause is combined by logical expression like OR or AND.
        If you need some other behaviour, it is possible to overwrite this method to implement your own
        matching or do some pre/post processing.

        Returns:
            sqlalchemy.sql.elements.BooleanClauseList: The combined clause blocks which wrapped in a
                sqlalchemy readable way
        """
        if len(self.clauses) == 1:
            clause = self.clauses[0]
        elif len(self.clauses) == 0:
            clause = None
        else:
            if self.mode == 'OR':
                clause = or_(*self.clauses)
            elif self.mode == 'AND':
                clause = and_(*self.clauses)
            else:
                raise HTTPBadRequest(
                    'The mode "{mode}" you passed is not implemented.'.format(mode=self.mode)
                )
        return clause


class Filter(object):

    def __init__(self, model_description, definition=None):
        """
        The class which represents the filter.

        Args:
            definition (dict): The values which are assigned to the object. The definition of the Filter.
                It has to be dict like {"mode": "OR/AND", "clauses": []}.
                The clauses are also dict objects with the pattern:
                    {
                        "column_name": "<name>",
                        "operator": "<see static method decide_operator for further detail>",
                        "value":<value>
                    }
                It is possible to pack a definition of filter inside the clause array.
                This enables complex queries.
            model_description (pyramid_georest.lib.description.ModelDescription): The description of the model
                which is being filtered.
        """

        if definition is None:
            definition = {}

        self.definition = FilterBlock(model_description, definition)

    def __str__(self):
        """

        :return: The string representation of the object
        :rtype: str
        """
        filter_text = str(self.definition.clause)
        return "Filter: {filter_text}".format(filter_text=filter_text)

    def filter(self, query):
        """
        The actual filter execution against the database via the constructed clause from the
        FilterDefinition object.

        :param query: The query where the filter should be applied to.
        :type query: sqlalchemy.orm.query.Query
        :return: The query with the applied filter
        :rtype: sqlalchemy.orm.query.Query
        """
        # print self.definition.clause
        if self.definition.clause is not None:
            query = query.filter(self.definition.clause)
        return query


class Service(object):

    def __init__(self, model, renderer_proxy=None, adapter_proxy=None):
        """
        A object which represents an restful service. It offers all the necessary methods and is able to
        consume a renderer proxy. This way we assure a plug able system to use custom renderers.
        If some custom behaviour is wanted at all, you can achieve this by subclassing this class and
        adding some post or pre processing to the desired method.

        :param model: The model for which the service will be created for.
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        :param renderer_proxy: A renderer proxy may be passed to achieve custom rendering
        :type renderer_proxy: RenderProxy or None
        :param adapter_proxy: An adapter which provides special client side library handling. It is a
            AdapterProxy per default.
        :type adapter_proxy: AdapterProxy or None
        """
        self.orm_model = model
        self.model_description = ModelDescription(self.orm_model)
        self.primary_key_names = self.model_description.primary_key_column_names
        self.name = self.name_from_definition(
            self.model_description.schema_name,
            self.model_description.table_name
        )
        if renderer_proxy is None:
            self.renderer_proxy = RenderProxy()
        else:
            self.renderer_proxy = renderer_proxy

        if adapter_proxy is None:
            self.adapter_proxy = AdapterProxy()
        else:
            self.adapter_proxy = adapter_proxy

    @staticmethod
    def name_from_definition(schema_name, table_name):
        """
        Little helper method to get a comma separated string of schema and table name.

        :param schema_name: The schema name
        :type schema_name: str
        :param table_name: The table name
        :type table_name: str
        :return: schema name and table name concatenated in one string separated by comma.
        :rtype: str
        """
        return '{0},{1}'.format(
            schema_name,
            table_name
        )

    def record_by_primary_keys_(self, session, primary_keys):
        query = session.query(self.orm_model)
        model_description = ModelDescription(self.orm_model)
        model_primary_keys = model_description.primary_key_columns.items()
        if len(primary_keys) != len(model_primary_keys):
            hint_text = "The number of passed primary keys mismatch the model given. Can't complete the " \
                        "request. Sorry..."
            log.error(hint_text)
            raise HTTPBadRequest(
                detail=hint_text
            )
        for index, requested_primary_key in enumerate(primary_keys):
            query = query.filter(model_primary_keys[index][1] == requested_primary_key)
        try:
            result = query.one()
            return result
        except MultipleResultsFound as e:
            hint_text = "Strange thing happened... Found more than one record for the primary key(s) " \
                        "you passed."
            log.error('{text}, Original error was: {error}'.format(text=hint_text, error=e))
            raise HTTPBadRequest(
                detail=hint_text
            )

    def handle_json_(self, orm_object, feature):
        """
        Method to assign values from passed json feature to the corresponding model object. It takes care of
        correctly handle geometry values.

        :param orm_object: The orm model object which the values should be assigned to.
        :type orm_object: sqlalchemy.ext.declarative.DeclarativeMeta
        :param feature: The feature which contains the values to be assigned to model instance.
        :type feature: dict
        """
        # At this moment there is no check for valid json data this leads to normal
        # behaving process, but no data will be written at all because the keys are not matching.
        for key in feature:
            value = feature[key]
            setattr(orm_object, key, self.geometry_treatment_(key, value))

    def handle_geojson_(self, orm_object, feature):
        """
        Method to assign values from passed geojson feature to the corresponding model object. It takes care
        of correctly handle geometry values.

        :param orm_object: The orm model object which the values should be assigned to.
        :type orm_object: sqlalchemy.ext.declarative.DeclarativeMeta
        :param feature: The feature which contains the values to be assigned to model instance.
        :type feature: dict
        """
        properties = feature.get('properties')
        for key in properties:
            value = properties[key]
            setattr(orm_object, key, value)
        geometry = feature.get('geometry')
        # GeoJson supports only one geometry attribute per feature, so we use the first geometry
        # column from model description... Not the best way but as long we have only one geometry
        # attribute per table it will work
        geometry_column_name = self.model_description.geometry_column_names[0]
        concrete_wkt = self.geometry_treatment_(geometry_column_name, asShape(geometry).wkt)
        setattr(orm_object, geometry_column_name, concrete_wkt)

    def geometry_treatment_(self, key, value):
        if value is not None and key in self.model_description.geometry_column_names:
            return WKTElement(
                value,
                self.model_description.column_descriptions.get(key).get('srid')
            )
        else:
            return value

    def read(self, session, request, rest_filter=None, offset=None, limit=None, order_by=None,
             direction=None):
        """
        The method which is used by the api to read a bunch of records from the database.

        Args:
            session (sqlalchemy.orm.Session): The session which is uesed to emit the query.
            request (pyramid.request.Request): The request which comes all the way through the application
                from the client
            rest_filter (pyramid_georest.lib.rest.Filter or None): The Filter which might be applied to the
                query in addition.
            offset (int or None): The offset which is used for paging reasons. It is only applied if limit is
                present too.
            limit (int or None): The limit which is used for paging reason. It is only applied of offest is
                present too.
            order_by (unicode or None): The column name which the sort is assigned to. It is only used if
                direction is present too.
            direction (unicode or None): The direction which is used for sorting. It is only used if order_by
                is present too.

        Returns:
             list of sqlalchemy.ext.declarative.DeclarativeMeta: A list of database records found for the
                request.
        """
        query = session.query(self.orm_model)
        if rest_filter is not None:
            query = rest_filter.filter(query)
        if isinstance(order_by, unicode) and isinstance(direction, unicode):
            column = self.model_description.column_classes.get(order_by)
            if direction in DIRECTION_ASC:
                query = query.order_by(asc(column))
            elif direction in DIRECTION_DESC:
                query = query.order_by(desc(column))
        if isinstance(offset, int) and isinstance(limit, int):
            query = query.offset(offset)
            query = query.limit(limit)
        results = query.all()
        return results

    def count(self, session, request, rest_filter=None):
        """
        The method which is used by the api to count the number of records in the database.

        Args:
            session (sqlalchemy.orm.Session): The session which is uesed to emit the query.
            request (pyramid.request.Request): The request which comes all the way through the application
                from the client
            rest_filter (pyramid_georest.lib.rest.Filter or None): The Filter which might be applied to the
                query in addition.

        Returns:
             int: The count of records found in the database.
        """
        query = session.query(self.orm_model)
        if rest_filter is not None:
            query = rest_filter.filter(query)
        count = query.count()
        return count

    def show(self, session, request, primary_keys):
        """
        The method which is used by the api to read exact one record from the database.

        Args:
            session (sqlalchemy.orm.Session): The sqlalchemy session object
            request (pyramid.request.Request): The request which comes all the way through the application
            from the client
            primary_keys (list of str): The primary keys which are used to filter the exact element.

        Returns:
             list of sqlalchemy.ext.declarative.DeclarativeMeta: A list of database records found for the
                request.
        """
        result = self.record_by_primary_keys_(session, primary_keys)
        return [result]

    def create(self, session, request, feature, passed_format):
        """
        The method which is used by the api to create exact one record in the database.

        Args:
            request (pyramid.request.Request): The request which comes all the way through the application
            from the client
            session (sqlalchemy.orm.Session): The sqlalchemy session object
            feature (dict): The feature which should be created in database.
            passed_format (str): The format which the feature is constructed of.

        Returns:
            list of sqlalchemy.ext.declarative.DeclarativeMeta: A list of database records found for the
                request.
        """
        orm_object = self.orm_model()
        if passed_format == 'json':
            self.handle_json_(orm_object, feature)
        elif passed_format == 'geojson':
            self.handle_geojson_(orm_object, feature)
        else:
            hint_text = 'The Format "{format}" is not defined for this service. Sorry...'.format(
                format=passed_format
            )
            log.error(hint_text)
            raise HTTPNotFound(
                detail=hint_text
            )
        session.add(orm_object)
        session.flush()
        return [orm_object]

    def update(self, session, request, primary_keys, feature, passed_format):
        """
        The method which is used by the api to update exact one record in the database.

        Args:
            session (sqlalchemy.orm.Session): The sqlalchemy session object
            request (pyramid.request.Request): The request which comes all the way through the application
            from the client
            primary_keys (list of str): The primary keys which are used to filter the exact element.
            feature (dict): The feature which should be updated in database.
            passed_format (str): The format which the feature is constructed of.

        Returns:
            list of sqlalchemy.ext.declarative.DeclarativeMeta: A list of database records found for the
                request.
        """
        orm_object = self.record_by_primary_keys_(session, primary_keys)
        if passed_format == 'json':
            self.handle_json_(orm_object, feature)
        elif passed_format == 'geojson':
            self.handle_geojson_(orm_object, feature)
        else:
            hint_text = 'The Format "{format}" is not defined for this service. Sorry...'.format(
                format=passed_format
            )
            log.error(hint_text)
            raise HTTPNotFound(
                detail=hint_text
            )
        session.add(orm_object)
        session.flush()
        return [orm_object]

    def delete(self, session, request, primary_keys):
        """
        The method which is used by the api to delete exact one record in the database.

        Args:
            session (sqlalchemy.orm.Session): The sqlalchemy session object
            request (pyramid.request.Request): The request which comes all the way through the application
            from the client
            primary_keys (list of str): The primary keys which are used to filter the exact element.

        Returns:
             list of sqlalchemy.ext.declarative.DeclarativeMeta: A list of database records found for the
                request.
        """
        result = self.record_by_primary_keys_(session, primary_keys)
        session.delete(result)
        session.flush()
        return [result]

    def model(self, request):
        """
        The method which is used by the api to deliver a machine readable and serializable description of
        the underlying database table/model.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: The model description of this service.
        :rtype: pyramid_georest.lib.description.ModelDescription
        """
        return self.model_description

    def adapter(self, request):
        """
        The method which is used by the api to deliver a client side usable adapter to handle the REST API.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: The model description of this service.
        :rtype: pyramid_georest.lib.description.ModelDescription
        """
        return self.model_description


class Api(object):

    def __init__(self, url, config, name, read_method='GET', read_filter_method='POST', create_method='POST',
                 update_method='PUT', delete_method='DELETE'):
        """
        A Object which holds the connection to the database and arbitrary numbers of services. It works
        like a proxy for the request. It decides which service will be finally called by reading
        the requested url parts and calls the appropriate service method.

        In addition you can implement api wide behaviour like authorization be subclassing this class
        and adding some pre or post processing to the particular methods.

        :param url: The connection string which is used to let the api connect with the desired database.
        It must have the form as described here:
        http://docs.sqlalchemy.org/en/latest/core/engines.html
        :type url: str
        :param config: The config of the hosting pyramid application.
        :type config: pyramid.config.Configurator
        :param name: The name which is used internally as an identifier of the api, to make it selectable
        between other api's. This name must be unique all over the application. If not an error will be
        thrown on application start up.
        :type name: str
        :param read_method: The HTTP method which is used to match the routing to the API.
        :type read_method: str
        :param read_filter_method: The HTTP method which is used to match the routing to the API.
        :type read_filter_method: str
        :param create_method: The HTTP method which is used to match the routing to the API.
        :type create_method: str
        :param update_method: The HTTP method which is used to match the routing to the API.
        :type update_method: str
        :param delete_method: The HTTP method which is used to match the routing to the API.
        :type delete_method: str
        :raises: LookupError
        """
        self.read_method = read_method
        self.read_filter_method = read_filter_method
        self.create_method = create_method
        self.update_method = update_method
        self.delete_method = delete_method

        connection_already_exists = False
        connections = config.registry.pyramid_georest_database_connections
        for key in connections:
            if url in key:
                connection_already_exists = True
                self.connection = connections[key]

        if not connection_already_exists:
            self.connection = Connection(url)
            config.registry.pyramid_georest_database_connections[url] = self.connection

        self.services = {}
        self.name = check_route_prefix(config.route_prefix) + name
        self.pure_name = name

        if self.name not in config.registry.pyramid_georest_apis:
            config.registry.pyramid_georest_apis[self.name] = self
            create_api_routing(config, self)
            config.commit()
        else:
            log.error(
                "The Api-Object you created seems to already exist in the registry. It has to "
                "be unique at all. Couldn't be added. Sorry..."
            )
            raise LookupError()

    def add_service(self, service):
        """
        Add's a service to the api.

        :param service: The service which should be added to the api.
        :type service: Service
        :raises: LookupError
        """
        if service.name not in self.services:
            self.services[service.name] = service
        else:
            log.error(
                "The Service {name} was defined for this API already. Use the defined one.".format(
                    name=service.name
                )
            )
            raise LookupError()

    def provide_session(self, request):
        """
        This method provides a usable SQLAlchemy session instance. It is ensured, that this session is doomed
        independent from the behavior of the request (it installs a finished listener to the request)


        :param request: The request of the pyramid web framework
        :type request: Request
        :return: a usable instance of a SQLAlchemy Session
        :rtype : Session
        """
        session_instance = self.connection.session()
        inner_scoped_session = self.connection.session

        def cleanup(request):
            if request.exception is None:
                transaction.commit()
            else:
                transaction.abort()
            inner_scoped_session.remove()

        request.add_finished_callback(cleanup)

        return session_instance

    def find_service_by_definition(self, schema_name, table_name):
        """
        Little helper method to obtain a service from the api's service list by it's unique schema+table name
        combination.

        :param schema_name: str
        :param table_name: str
        :return: Service or None
        :rtype: Service
        """
        return self.services.get(Service.name_from_definition(schema_name, table_name))

    def find_service_by_request(self, request):
        """
        Little helper method to scrabble the requested service directly from the url which was requested.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: The service.
        :rtype: Service
        :raises: HTTPNotFound
        """
        schema_name = request.matchdict['schema_name']
        table_name = request.matchdict['table_name']
        service = self.find_service_by_definition(schema_name, table_name)
        if service is None:
            hint_text = 'Service with schema {schema_name} and table {table_name} could not be found.'.format(
                schema_name=schema_name,
                table_name=table_name
            )
            log.error(hint_text)
            raise HTTPNotFound(
                detail=hint_text
            )
        request.registry.pyramid_georest_requested_service = service
        return service

    def read(self, request):
        """
        The api wide method to receive the read request and passing it to the correct service. At this
        point it is possible to implement some post or pre processing by overwriting this method.
        The most common use case for this will be the implementation of an authorisation mechanism which has
        influence on the whole api. To have influence on special services please see the service class
        implementations read method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        service = self.find_service_by_request(request)
        request.registry.pyramid_georest_requested_api = self
        session = self.provide_session(request)
        rest_filter = None
        if request.method == request.registry.pyramid_georest_requested_api.read_filter_method:
            rest_filter = Filter(service.model_description, **request.json_body.get('filter'))
        offset = request.params.get('offset')
        limit = request.params.get('limit')
        order_by = request.params.get('order_by')
        direction = request.params.get('direction')
        if offset and limit:
            try:
                offset = int(offset)
            except ValueError as e:
                hint_txt = 'Value for offset has to be integer or a string which can be parsed as integer.'
                log.error(e)
                log.error(hint_txt)
                raise HTTPBadRequest(hint_txt)
            try:
                limit = int(limit)
            except ValueError as e:
                hint_txt = 'Value for limit has to be integer or a string which can be parsed as integer.'
                log.error(e)
                log.error(hint_txt)
                raise HTTPBadRequest(hint_txt)
        else:
            offset = None
            limit = None

        if order_by and direction:
            if not isinstance(order_by, unicode):
                hint_txt = 'Value for order_by has to be string.'
                log.error(hint_txt)
                raise HTTPBadRequest(hint_txt)
            if not isinstance(direction, unicode):
                hint_txt = 'Value for direction has to be string.'
                log.error(hint_txt)
                raise HTTPBadRequest(hint_txt)
            if direction not in DIRECTION_ASC + DIRECTION_DESC:
                raise HTTPBadRequest(
                    'The parameter direction has to be one of the values: {0}'.format(
                        DIRECTION_ASC + DIRECTION_DESC
                    )
                )
            if not service.model_description.is_valid_column(order_by):
                raise HTTPBadRequest('The parameter order_by has to be one of the models columns. The passed '
                                     'column name was {}'.format(order_by)
                                     )
        else:
            order_by = None
            direction = None

        results = service.read(session, request, rest_filter, offset=offset, limit=limit,
                               order_by=order_by, direction=direction)
        return service.renderer_proxy.render(request, results, service.model_description)

    def count(self, request):
        """
        The api wide method to receive the count request and passing it to the correct service. At this
        point it is possible to implement some post or pre processing by overwriting this method.
        The most common use case for this will be the implementation of an authorisation mechanism which has
        influence on the whole api. To have influence on special services please see the service class
        implementations read method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        service = self.find_service_by_request(request)
        request.registry.pyramid_georest_requested_api = self
        session = self.provide_session(request)
        rest_filter = None
        if request.method == request.registry.pyramid_georest_requested_api.read_filter_method:
            rest_filter = Filter(service.model_description, **request.json_body.get('filter'))
        count = service.count(session, request, rest_filter)
        return count

    def show(self, request):
        """
        The api wide method to receive the show request and passing it to the correct service. At this
        point it is possible to implement some post or pre processing by overwriting this method.
        The most common use case for this will be the implementation of an authorisation mechanism
        which has influence on the whole api. To have influence on special services please see the service
        class implementations show method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        service = self.find_service_by_request(request)
        request.registry.pyramid_georest_requested_api = self
        session = self.provide_session(request)
        primary_keys = request.matchdict['primary_keys']
        results = service.show(session, request, primary_keys)
        return service.renderer_proxy.render(request, results, service.model_description)

    def create(self, request):
        """
        The api wide method to receive the create request and passing it to the correct service.
        At this point it is possible to implement some post or pre processing by overwriting this method.
        The most common use case for this will be the implementation of an authorisation mechanism which
        has influence on the whole api. To have influence on special services please see the service class
        implementations create method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        service = self.find_service_by_request(request)
        request.registry.pyramid_georest_requested_api = self
        session = self.provide_session(request)
        passed_format = request.matchdict['format']
        if request.json_body.get('feature'):
            feature = request.json_body.get('feature')
            results = service.create(session, request, feature, passed_format)
            request.response.status_int = 201
            return service.renderer_proxy.render(request, results, service.model_description)
        else:
            raise HTTPBadRequest('No features where found in request...')

    def delete(self, request):
        """
        The api wide method to receive the delete request and passing it to the correct service.
        At this point it is possible to implement some post or pre processing by overwriting this method.
        The most common use case for this will be the implementation of an authorisation mechanism which has
        influence on the whole api. To have influence on special services please see the service class
        implementations delete method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        service = self.find_service_by_request(request)
        request.registry.pyramid_georest_requested_api = self
        session = self.provide_session(request)
        primary_keys = request.matchdict['primary_keys']
        results = service.delete(session, request, primary_keys)
        return service.renderer_proxy.render(request, results, service.model_description)

    def update(self, request):
        """
        The api wide method to receive the update request and passing it to the correct service.
        At this point it is possible to implement some post or pre processing by overwriting this method.
        The most common use case for this will be the implementation of an authorisation mechanism which has
        influence on the whole api. To have influence on special services please see the service class
        implementations update method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        service = self.find_service_by_request(request)
        request.registry.pyramid_georest_requested_api = self
        session = self.provide_session(request)
        primary_keys = request.matchdict['primary_keys']
        passed_format = request.matchdict['format']
        if request.json_body.get('feature'):
            feature = request.json_body.get('feature')
            results = service.update(session, request, primary_keys, feature, passed_format)
            request.response.status_int = 202
            return service.renderer_proxy.render(request, results, service.model_description)
        else:
            raise HTTPBadRequest('No features where found in request...')

    def model(self, request):
        """
        The api wide method to receive the model request and passing it to the correct service.
        At this point it is possible to implement some post or pre processing by overwriting this method.
        The most common use case for this will be the implementation of an authorisation mechanism which
        has influence on the whole api. To have influence on special services please see the service class
        implementations model method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        :raises: HTTPNotFound
        """
        service = self.find_service_by_request(request)
        request.registry.pyramid_georest_requested_api = self
        response_format = request.matchdict['format']
        model = service.model(request)
        if response_format == 'json':
            return render_to_response(
                'geo_restful_model_json',
                model,
                request=request
            )
        elif response_format == 'xml':
            return render_to_response(
                'geo_restful_model_xml',
                model,
                request=request
            )
        else:
            hint_text = 'The Format "{format}" is not defined for this service. Sorry...'.format(
                format=response_format
            )
            log.error(hint_text)
            raise HTTPNotFound(
                detail=hint_text
            )

    def adapter(self, request):
        """
        The api wide method to receive the adapter request and passing it to the correct service.
        At this point it is possible to implement some post or pre processing by overwriting this method.
        The most common use case for this will be the implementation of an authorisation mechanism which
        has influence on the whole api. To have influence on special services please see the service class
        implementations adapter method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        service = self.find_service_by_request(request)
        request.registry.pyramid_georest_requested_api = self
        model = service.model(request)
        return service.adapter_proxy.render(request, model)
