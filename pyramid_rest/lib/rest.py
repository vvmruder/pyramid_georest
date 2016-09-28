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
from pyramid_rest.lib.description import ModelDescription
from pyramid_rest.lib.renderer import RenderProxy
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound
from pyramid_rest.lib.database import Connection

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'

log = logging.getLogger('pyramid_rest')


class Service(object):

    def __init__(self, model, renderer_proxy=None):
        """

        :param model:
        :type model: sqlalchemy.ext.declarative.DeclarativeMeta
        :param schema_name:
        :type schema_name: str
        :param table_name: Str
        :type table_name: str
        :param primary_key_names: list of Str
        :type primary_key_names: list of str
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

        :param schema_name: str
        :param table_name: str
        :return:
        """
        return '{0},{1}'.format(
            schema_name,
            table_name
        )

    def read(self, request, session):
        results = session.query(self.orm_model).all()
        return self.renderer_proxy.render(request, results, self.orm_model)

    def show(self, request, session):
        requested_primary_keys = request.matchdict['primary_keys']
        model_description = ModelDescription(self.orm_model)
        model_primary_keys = model_description.primary_key_columns.items()
        if len(requested_primary_keys) != len(model_primary_keys):
            text = "The number of passed primary keys mismatch the model given. Can't complete the request. Sorry..."
            log.error(text)
            raise HTTPBadRequest(
                detail=text
            )
        query = session.query(self.orm_model)
        for index, requested_primary_key in enumerate(requested_primary_keys):
            query = query.filter(model_primary_keys[index][1] == requested_primary_key)
        try:
            result = query.one()
            return self.renderer_proxy.render(request, [result], self.orm_model)
        except MultipleResultsFound, e:
            text = "Strange thing happened... Found more than one record for the primary key(s) you passed."
            log.error('{text}, Original error was: {error}'.format(text=text, error=e))
            raise HTTPBadRequest(
                detail=text
            )

    def create(self, request, session):
        pass

    def delete(self, request, session):
        pass

    def update(self, request, session):
        pass

    def model(self, request):
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
            text = 'The Format "{format}" is not defined for this service. Sorry...'.format(
                format=response_format
            )
            log.error(text)
            raise HTTPNotFound(
                detail=text
            )


class Api(object):

    def __init__(self, url, config, name):
        connection_already_exists = False
        for key, value in config.registry.pyramid_rest_database_connections.iteritems():
            if url in key:
                connection_already_exists = True
                self.connection = value

        if not connection_already_exists:
            self.connection = Connection(url)
            config.registry.pyramid_rest_database_connections[url] = self.connection

        self.services = {}

        if name not in config.registry.pyramid_rest_apis:
            config.registry.pyramid_rest_apis[name] = self
        else:
            log.error(
                "The Api-Object you created seems to already exist in the registry. It has to be unique at all. "
                "Couldn't be added. Sorry..."
            )
            raise LookupError()

    def add_service(self, service):
        """

        :param service: Service
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

        :param schema_name: str
        :param table_name: str
        :return: Service or None
        :rtype: Service
        """
        return self.services.get(Service.name_from_definition(schema_name, table_name))

    def find_service_by_request(self, request):
        schema_name = request.matchdict['schema_name']
        table_name = request.matchdict['table_name']
        service = self.find_service_by_definition(schema_name, table_name)
        if service is None:
            text = 'Service with schema {schema_name} and table {table_name} could not be found.'.format(
                schema_name=schema_name,
                table_name=table_name
            )
            log.error(text)
            raise HTTPNotFound(
                detail=text
            )
        return service

    def read(self, request):
        return self.find_service_by_request(request).read(
            request,
            self.provide_session(request)
        )

    def show(self, request):
        return self.find_service_by_request(request).show(
            request,
            self.provide_session(request)
        )

    def create(self, request):
        return self.find_service_by_request(request).create(
            request,
            self.provide_session(request)
        )

    def delete(self, request):
        return self.find_service_by_request(request).delete(
            request,
            self.provide_session(request)
        )

    def update(self, request):
        return self.find_service_by_request(request).update(
            request,
            self.provide_session(request)
        )

    def model(self, request):
        return self.find_service_by_request(request).model(
            request
        )
