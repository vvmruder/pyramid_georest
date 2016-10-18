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
import logging
import transaction
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.request import Request
from pyramid_georest.lib.description import ModelDescription
from pyramid_georest.lib.renderer import RenderProxy
from pyramid_georest.lib.database import Connection
from pyramid_georest.routes import read_filter_method
from sqlalchemy import or_, and_
from sqlalchemy import cast
from sqlalchemy import String
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound
from geoalchemy2 import WKTElement

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'

log = logging.getLogger('pyramid_georest')


class FilterDefinition(object):

    def __init__(self, model_description, **kwargs):
        """
        This implements an object which is able to parse the filter definition passed as a dict. It is possible to
        construct arbitrary deep filters with this class.

        The main goal of the FilterDefinition is to have a parsing from dict to an object which holds the whole filter
        definition in an sqlalchemy consumable way.

        :param model_description: The description of the model which is being filtered.
        :type model_description: ModelDescription
        :param kwargs: The definition of the Filter. It has to be dict like {"mode": "OR/AND", "clauses": []}. The
        clauses are also dict objects with the pattern:
        {"column_name": "<name>", "operator": "<see static method decide_operator for further detail>", "value":<value>}
        It is possible to pack a definition of filter inside the clause array. This enables complex queries.
        :raises: HTTPBadRequest
        """
        self.model_description = model_description
        self.clause_blocks = []
        self.clause = None
        self.passed_filter_clauses = []
        for key, value in kwargs.iteritems():
            if key == 'mode':
                self.mode = value
            elif key == 'clauses':
                self.passed_filter_clauses = value
        for clause in self.passed_filter_clauses:
            if clause.get('mode', False):
                self.clause_blocks.append(FilterDefinition(self.model_description, **clause).clause)
            else:
                if clause.get('column_name', False):
                    column_name = clause.get('column_name')
                    column = model_description.column_classes.get(column_name)
                    column_description = self.model_description.column_descriptions.get(column_name)
                else:
                    raise HTTPBadRequest('somewhere in the filter the column name is missing!')
                if clause.get('operator', False):
                    operator = clause.get('operator')
                else:
                    raise HTTPBadRequest('somewhere in the filter the operator is missing!')
                if clause.get('value', False):
                    value = clause.get('value')
                else:
                    raise HTTPBadRequest('somewhere in the filter the value is missing!')
                # special handling for geometry columns
                if column_description.get('is_geometry_column'):
                    clause_construct = self.decide_multi_geometries(column_description, column, value, operator)
                else:
                    clause_construct = self.decide_operator(column, operator, value)
                self.clause_blocks.append(clause_construct)
                # print self.clause_blocks
        # print self.clause_blocks
        self.clause = self.decide_mode(self.mode, self.clause_blocks)
        # print type(self.clause)

    @staticmethod
    def decide_operator(column, operator, value):
        """
        This method is used by the filter object to make a simple matching between the passed operators and the
        operators which are useable for filtering against the database.
        There are only some base operators implemented by default. If you like some more specific ones feel free to
        subclass this class and overwrite this method with your special behaviour and maching.
        Note that this method does not only do the matching thing. It constructs the whole binary expression. So you can
        get some influence on this process too.

        :param column: The sqlalchemy column which the clause should be formed with.
        :type column: sqlalchemy.schema.Column
        :param operator: A boolean operator which is used to form the clause.
        :type operator: str
        :param value: The value which is used for comparison.
        :type value: Can be any base type
        :return: The clause element
        :rtype: sqlalchemy.sql.expression._BinaryExpression
        :raises: HTTPBadRequest
        """
        if operator == '=':
            clause = column == value
        elif operator == '==':
            clause = column == value
        elif operator == '<>':
            clause = column != value
        elif operator == '<':
            clause = column < value
        elif operator == '<=':
            clause = column <= value
        elif operator == '>':
            clause = column > value
        elif operator == '>=':
            clause = column >= value
        elif operator == 'LIKE':
            clause = cast(column, String(length=100)).like(str(value))
        elif operator == 'IN':
            clause = column.in_(str(value).split(','))
        elif operator == 'NULL':
            clause = column == None
        elif operator == 'NOT_NULL':
            clause = column != None
        else:
            raise HTTPBadRequest('The operator "{operator}" you passed is not implemented.'.format(operator=operator))
        return clause

    def decide_multi_geometries(self, column_description, column, value, operator):
        """
        This method decides if the clause will contain geometry collections (in the value or in the database or in
        both).
        If it does it is necessary to "unpack" all collections to make them valid for geometric operations in database.
        If it does not it uses a normal geometric operation.

        :param column_description: The machine readable description of the column.
        :type column_description: pyramid_georest.description.ColumnDescription
        :param column: The sqlalchemy column which the clause should be formed with.
        :type column: sqlalchemy.schema.Column
        :param value: The WKT geometry representation which is used for comparison.
        :type value: str
        :param operator: A geometric operation which is used to form the clause.
        :type operator: str
        :return: The clause element
        :rtype: sqlalchemy.sql.expression._BinaryExpression
        :raises: HTTPBadRequest
        """
        geometry_type = str(column_description.get('type')).upper()
        db_path_list = [
            self.model_description.schema_name,
            self.model_description.table_name,
            column_description.get('column_name')
        ]
        db_path = '.'.join(db_path_list)
        if geometry_type == 'GEOMETRYCOLLECTION' and 'GEOMETRYCOLLECTION' not in value:
            clause_construct = self.extract_geometry_collection_db(db_path, value, operator)
        elif 'GEOMETRYCOLLECTION' in value and geometry_type != 'GEOMETRYCOLLECTION':
            clause_construct = self.extract_geometry_collection_input(db_path, value, operator)
        elif 'GEOMETRYCOLLECTION' in value and geometry_type == 'GEOMETRYCOLLECTION':
            clause_construct = self.extract_geometry_collection_input_and_db(db_path, value, operator)
        elif geometry_type != 'GEOMETRYCOLLECTION' and 'GEOMETRYCOLLECTION' not in value:
            clause_construct = self.decide_geometric_operation(column, operator, value)
        else:
            hint_text = "You found some bad geometric circumstance. Sorry for that. We can't handle your " \
                        "request uses the operation {operation} on a geometric column with the type " \
                        "{geometry_type} and your passed geometry was of the value {value}. This is not " \
                        "supported in the moment.".format(
                            operation=operator,
                            geometry_type=geometry_type,
                            value=value
                        )
            raise HTTPBadRequest(hint_text)
        return clause_construct

    @staticmethod
    def decide_geometric_operation(column, operator, value):
        """
        Decides the simple cases of geometric filter operations.

        :param column: The sqlalchemy column which the clause should be formed with.
        :type column: sqlalchemy.schema.Column
        :param operator: A geometric operation which is used to form the clause.
        :type operator: str
        :param value: The WKT geometry representation which is used for comparison.
        :type value: str
        :return: The clause element
        :rtype: sqlalchemy.sql.expression._BinaryExpression
        :raises: HTTPBadRequest
        """
        if operator == 'INTERSECTS':
            clause = column.ST_Intersects(WKTElement(value, srid=2056))
        elif operator == 'TOUCHES':
            clause = column.ST_Touches(WKTElement(value, srid=2056))
        elif operator == 'COVERED_BY':
            clause = column.ST_CoveredBy(WKTElement(value, srid=2056))
        elif operator == 'WITHIN':
            clause = column.ST_DFullyWithin(WKTElement(value, srid=2056))
        else:
            raise HTTPBadRequest('The operator "{operator}" you passed is not implemented.'.format(operator=operator))
        return clause

    @staticmethod
    def extract_geometry_collection_db(db_path, value, operator):
        """
        Decides the geometry collections cases of geometric filter operations when the database contains multi
        geometries but the passed geometry does not.
        The multi geometry will be extracted to it's sub parts for operation.

        :param db_path: The point separated string of schema_name.table_name.column_name from which we can construct
         a correct SQL statement.
        :type db_path: str
        :param value: The WKT geometry representation which is used for comparison.
        :type value: str
        :param operator: A geometric operation which is used to form the clause.
        :type operator: str
        :return: The clause element.
        :rtype: sqlalchemy.sql.elements.BooleanClauseList
        :raises: HTTPBadRequest
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
        sql_text_point = '{0}(ST_CollectionExtract({1}, 1), ST_GeomFromText(\'{2}\', 2056))'.format(operator,
                                                                                                    db_path,
                                                                                                    value)
        sql_text_line = '{0}(ST_CollectionExtract({1}, 2), ST_GeomFromText(\'{2}\', 2056))'.format(operator,
                                                                                                   db_path,
                                                                                                   value)
        sql_text_polygon = '{0}(ST_CollectionExtract({1}, 3), ST_GeomFromText(\'{2}\', 2056))'.format(operator,
                                                                                                      db_path,
                                                                                                      value)
        clause_blocks = [
            text(sql_text_point),
            text(sql_text_line),
            text(sql_text_polygon)
        ]
        return or_(*clause_blocks)

    @staticmethod
    def extract_geometry_collection_input(db_path, value, operator):
        """
        Decides the geometry collections cases of geometric filter operations when the database contains multi
        geometries but the passed geometry does not.
        The multi geometry will be extracted to it's sub parts for operation.

        :param db_path: The point separated string of schema_name.table_name.column_name from which we can construct
         a correct SQL statement.
        :type db_path: str
        :param value: The WKT geometry representation which is used for comparison.
        :type value: str
        :param operator: A geometric operation which is used to form the clause.
        :type operator: str
        :return: The clause element.
        :rtype: sqlalchemy.sql.elements.BooleanClauseList
        :raises: HTTPBadRequest
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
        sql_text_point = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 1))'.format(operator,
                                                                                                    db_path,
                                                                                                    value)
        sql_text_line = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 2))'.format(operator,
                                                                                                   db_path,
                                                                                                   value)
        sql_text_polygon = '{0}({1}, ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 3))'.format(operator,
                                                                                                      db_path,
                                                                                                      value)
        clause_blocks = [
            text(sql_text_point),
            text(sql_text_line),
            text(sql_text_polygon)
        ]
        return or_(*clause_blocks)

    @staticmethod
    def extract_geometry_collection_input_and_db(db_path, value, operator):
        """
        Decides the geometry collections cases of geometric filter operations when the database contains multi
        geometries but the passed geometry does not.
        The multi geometry will be extracted to it's sub parts for operation.

        :param db_path: The point separated string of schema_name.table_name.column_name from which we can construct
         a correct SQL statement.
        :type db_path: str
        :param value: The WKT geometry representation which is used for comparison.
        :type value: str
        :param operator: A geometric operation which is used to form the clause.
        :type operator: str
        :return: The clause element.
        :rtype: sqlalchemy.sql.elements.BooleanClauseList
        :raises: HTTPBadRequest
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
        sql_text_point = '{0}(ST_CollectionExtract({1}, 1), ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 1))'.format(
            operator, db_path, value)
        sql_text_line = '{0}(ST_CollectionExtract({1}, 2), ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 2))'.format(
            operator, db_path, value)
        sql_text_polygon = '{0}(ST_CollectionExtract({1}, 3), ST_CollectionExtract(ST_GeomFromText(\'{2}\', 2056), 3))'.format(
            operator, db_path, value)
        clause_blocks = [
            text(sql_text_point),
            text(sql_text_line),
            text(sql_text_polygon)
        ]
        return or_(*clause_blocks)

    @staticmethod
    def decide_mode(mode, clause_blocks):
        """
        This method is used to match the mode and construct a clause list in which are each single filter clause is
        combined by logical expression like OR or AND.
        If you need some other behaviour, it is possible to overwrite this method to implement your own matching or do
        some pre/post processing.

        :param mode: The mode to combine the clause blocks.
        :type mode: str
        :param clause_blocks: The clause blocks which should be combined.
        :type clause_blocks: list of sqlalchemy.sql.expression._BinaryExpression
        :return: The combined clause blocks which wrapped in a sqlalchemy readable way
        :rtype: sqlalchemy.sql.elements.BooleanClauseList
        """
        if len(clause_blocks) == 1:
            clause = clause_blocks[0]
        else:
            if mode == 'OR':
                clause = or_(*clause_blocks)
            elif mode == 'AND':
                clause = and_(*clause_blocks)
            else:
                raise HTTPBadRequest(('The mode "{mode}" you passed is not implemented.'.format(mode=mode)))
        return clause


class Filter(object):

    def __init__(self, model_description, filter_definition_class=None, **kwargs):
        """
        Kind of an proxy class which is the gate to the concrete filter definition object. This enables us to add some
        pre/post processing.

        :param model: The model for which the service will be created for.
        :type model: ModelDescription
        :param filter_definition_class: A subclass type of FilterDefinition may be passed to override behaviour of
        filtering.
        :type filter_definition_class: class FilterDefinition
        :param kwargs:
        """
        self.model_description = model_description
        if filter_definition_class is None:
            self.filter_definition_class = FilterDefinition
        else:
            self.filter_definition_class = filter_definition_class
        for key, value in kwargs.iteritems():
            if key == 'definition':
                self.definition = self.filter_definition_class(model_description, **value)
            else:
                setattr(self, key, value)

    def __str__(self):
        """

        :return: The string representation of the object
        :rtype: str
        """
        filter_text = str(self.definition.clause)
        return "Filter: {filter_text}".format(filter_text=filter_text)

    def filter(self, query):
        """
        The actual filter execution against the database via the constructed clause from the FilterDefinition object.

        :param query: The query where the filter should be applied to.
        :type query: sqlalchemy.orm.query.Query
        :return: The query with the applied filter
        :rtype: sqlalchemy.orm.query.Query
        """
        # print self.definition.clause
        query = query.filter(self.definition.clause)
        return query


class Service(object):

    def __init__(self, model, renderer_proxy=None):
        """
        A object which represents an restful service. It offers all the necessary methods and is able to consume a
        renderer proxy. This way we assure a plug able system to use custom renderers. If some custom behaviour is
        wanted at all, you can achieve this by subclassing this class and adding some post or pre processing to the
        desired method.

        :param model: The model for which the service will be created for.
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        :param renderer_proxy: A renderer proxy may be passed to achieve custom rendering
        :type renderer_proxy: RenderProxy or None
        """
        self.orm_model = model
        self.model_description = ModelDescription(self.orm_model)
        self.primary_key_names = self.model_description.primary_key_column_names
        self.name = self.name_from_definition(self.model_description.schema_name, self.model_description.table_name)
        if renderer_proxy is None:
            self.renderer_proxy = RenderProxy()
        else:
            self.renderer_proxy = renderer_proxy

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

    def read(self, request, session):
        """
        The method which is used by the api to read a bunch of records from the database.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :param session: The session which is uesed to emit the query.
        :type session: sqlalchemy.orm.Session
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        query = session.query(self.orm_model)
        if request.method == read_filter_method:
            rest_filter = Filter(self.model_description, **request.json_body.get('filter'))
            query = rest_filter.filter(query)
        results = query.all()
        return self.renderer_proxy.render(request, results, self.model_description)

    def show(self, request, session):
        """
        The method which is used by the api to read exact one record from the database.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :param session: The session which is uesed to emit the query.
        :type session: sqlalchemy.orm.Session
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        :raises: HTTPBadRequest
        """
        requested_primary_keys = request.matchdict['primary_keys']
        model_description = ModelDescription(self.orm_model)
        model_primary_keys = model_description.primary_key_columns.items()
        if len(requested_primary_keys) != len(model_primary_keys):
            hint_text = "The number of passed primary keys mismatch the model given. Can't complete the request. Sorry..."
            log.error(hint_text)
            raise HTTPBadRequest(
                detail=hint_text
            )
        query = session.query(self.orm_model)
        for index, requested_primary_key in enumerate(requested_primary_keys):
            query = query.filter(model_primary_keys[index][1] == requested_primary_key)
        try:
            result = query.one()
            return self.renderer_proxy.render(request, [result], self.model_description)
        except MultipleResultsFound, e:
            hint_text = "Strange thing happened... Found more than one record for the primary key(s) you passed."
            log.error('{text}, Original error was: {error}'.format(text=hint_text, error=e))
            raise HTTPBadRequest(
                detail=hint_text
            )

    def create(self, request, session):
        """
        The method which is used by the api to create exact one record in the database.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :param session: The session which is uesed to emit the query.
        :type session: sqlalchemy.orm.Session
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        pass

    def delete(self, request, session):
        """
        The method which is used by the api to delete exact one record in the database.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :param session: The session which is uesed to emit the query.
        :type session: sqlalchemy.orm.Session
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        pass

    def update(self, request, session):
        """
        The method which is used by the api to update exact one record in the database.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :param session: The session which is uesed to emit the query.
        :type session: sqlalchemy.orm.Session
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        pass

    def model(self, request):
        """
        The method which is used by the api to deliver a machine readable and serializable description of the underlying
        database table/model.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :param session: The session which is uesed to emit the query.
        :type session: sqlalchemy.orm.Session
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        :raises: HTTPNotFound
        """
        response_format = request.matchdict['format']
        if response_format == 'json':
            return render_to_response(
                'model_restful_json',
                self.model_description,
                request=request
            )
        elif response_format == 'xml':
            return render_to_response(
                'model_restful_xml',
                self.model_description,
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


class Api(object):

    def __init__(self, url, config, name):
        """
        A Object which holds the connection to the database and arbitrary numbers of services. It works like a proxy
        for the request. It decides which service will be finally called by reading the requested url parts and calls
        the appropriate service method.

        In addition you can implement api wide behaviour like authorization be subclassing this class and adding some
        pre or post processing to the particular methods.

        :param url: The connection string which is used to let the api connect with the desired database.
        It must have the form as described here:
        http://docs.sqlalchemy.org/en/latest/core/engines.html
        :type url: str
        :param config: The config of the hosting pyramid application.
        :type config: pyramid.config.Configurator
        :param name: The name which is used internally as an identifier of the api, to make it selectable between other
        api's. This name must be unique all over the application. If not an error will be thrown on application start
        up.
        :type name: str
        :raises: LookupError
        """
        connection_already_exists = False
        for key, value in config.registry.pyramid_georest_database_connections.iteritems():
            if url in key:
                connection_already_exists = True
                self.connection = value

        if not connection_already_exists:
            self.connection = Connection(url)
            config.registry.pyramid_georest_database_connections[url] = self.connection

        self.services = {}

        if name not in config.registry.pyramid_georest_apis:
            config.registry.pyramid_georest_apis[name] = self
        else:
            log.error(
                "The Api-Object you created seems to already exist in the registry. It has to be unique at all. "
                "Couldn't be added. Sorry..."
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
        return service

    def read(self, request):
        """
        The api wide method to receive the read request and passing it to the correct service. At this point it is
        possible to implement some post or pre processing by overwriting this method. The most common use case for this
        will be the implementation of an authorisation mechanism which has influence on the whole api. To have influence
        on special services please see the service class implementations read method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.find_service_by_request(request).read(
            request,
            self.provide_session(request)
        )

    def show(self, request):
        """
        The api wide method to receive the show request and passing it to the correct service. At this point it is
        possible to implement some post or pre processing by overwriting this method. The most common use case for this
        will be the implementation of an authorisation mechanism which has influence on the whole api. To have influence
        on special services please see the service class implementations read method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.find_service_by_request(request).show(
            request,
            self.provide_session(request)
        )

    def create(self, request):
        """
        The api wide method to receive the create request and passing it to the correct service. At this point it is
        possible to implement some post or pre processing by overwriting this method. The most common use case for this
        will be the implementation of an authorisation mechanism which has influence on the whole api. To have influence
        on special services please see the service class implementations read method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.find_service_by_request(request).create(
            request,
            self.provide_session(request)
        )

    def delete(self, request):
        """
        The api wide method to receive the delete request and passing it to the correct service. At this point it is
        possible to implement some post or pre processing by overwriting this method. The most common use case for this
        will be the implementation of an authorisation mechanism which has influence on the whole api. To have influence
        on special services please see the service class implementations read method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.find_service_by_request(request).delete(
            request,
            self.provide_session(request)
        )

    def update(self, request):
        """
        The api wide method to receive the update request and passing it to the correct service. At this point it is
        possible to implement some post or pre processing by overwriting this method. The most common use case for this
        will be the implementation of an authorisation mechanism which has influence on the whole api. To have influence
        on special services please see the service class implementations read method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.find_service_by_request(request).update(
            request,
            self.provide_session(request)
        )

    def model(self, request):
        """
        The api wide method to receive the model request and passing it to the correct service. At this point it is
        possible to implement some post or pre processing by overwriting this method. The most common use case for this
        will be the implementation of an authorisation mechanism which has influence on the whole api. To have influence
        on special services please see the service class implementations read method.

        :param request: The request which comes all the way through the application from the client
        :type request: pyramid.request.Request
        :return: An pyramid response object
        :rtype: pyramid.response.Response
        """
        return self.find_service_by_request(request).model(
            request
        )
