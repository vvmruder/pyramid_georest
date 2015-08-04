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
from geoalchemy import WKBSpatialElement
from shapely import wkt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest, HTTPServerError
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker, Session
from pyramid.config import Configurator
from pyramid.request import Request

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'


class Rest(object):
    """
    Offers an interface to make SQLAlchemy objects restful in a pyramids web framework way
    """
    not_found_text = u'<h2>No element was found in database, with primary key: ({0})</h2>'
    bad_text = u'<h2>You submitted data which is incorrect. Please check the shipped parameter of your request.</h2>'
    integrity_error_txt = u'<h2>Your submitted data was corrupt. This usually means your data hurts some database ' \
                          u'constrains</h2>'

    def __init__(self, engine, model, config):
        """

        Creates an object which handles all things to do to provide an rest interface for the passed:
         - sql-alchemy database engine
         - sql-alchemy model (which MUST be created with the Base class provided in this package's models script!!!)
         - the pyramid config object

        Please refer to the README.rst of this package to learn more about the usage.

        :param engine: The engine which the RESTful interface should be bound to
        :type engine: Engine
        :param model: The mapper representing the database table, this must be an child class of the Base defined in .models!
        :type model: Base
        :param config: The Configurator of the underling pyramid web app
        :type config: Configurator
        """

        self.engine = engine
        self.model = model

        read_json_path = '/' + model.database_path().replace('.', '/') + '/read.json'

        read_html_path = '/' + model.database_path().replace('.', '/') + '/read'

        read_one_json_path = '/' + model.database_path().replace('.', '/') + '/read' + self.primary_key_to_url() + '.json'

        read_one_html_path = '/' + model.database_path().replace('.', '/') + '/read' + self.primary_key_to_url()

        create_path = '/' + model.database_path().replace('.', '/') + '/create'

        update_path = '/' + model.database_path().replace('.', '/') + '/update' + self.primary_key_to_url()

        delete_path = '/' + model.database_path().replace('.', '/') + '/delete' + self.primary_key_to_url()

        count = '/' + model.database_path().replace('.', '/') + '/count'

        model_json = '/' + model.database_path().replace('.', '/') + '/model.json'

        config.add_route(read_json_path, read_json_path)
        config.add_view(self.read, renderer='restful_json', route_name=read_json_path, request_method='GET')

        config.add_route(read_one_json_path, read_one_json_path)
        config.add_view(self.read_one, renderer='restful_json', route_name=read_one_json_path, request_method='GET')

        config.add_route(create_path, create_path)
        config.add_view(self.create, renderer='restful_json', route_name=create_path, request_method='POST')

        config.add_route(update_path, update_path)
        config.add_view(self.update, renderer='restful_json', route_name=update_path, request_method='POST')

        config.add_route(delete_path, delete_path)
        config.add_view(self.delete, renderer='restful_json', route_name=delete_path, request_method='GET')

        config.add_route(count, count)
        config.add_view(self.count, renderer='jsonp', route_name=count, request_method='GET')

        config.add_route(model_json, model_json)
        config.add_view(self.description, renderer='jsonp', route_name=model_json, request_method='GET')

        config.add_route(read_html_path, read_html_path)
        config.add_view(
            self.read,
            renderer='pyramid_rest:templates/read.mako',
            route_name=read_html_path,
            request_method='GET'
        )

        config.add_route(read_one_html_path, read_one_html_path)
        config.add_view(
            self.read_one,
            renderer='pyramid_rest:templates/read.mako',
            route_name=read_one_html_path,
            request_method='GET'
        )

        config.registry.pyramid_rest_services.append(model.database_path().replace('.', '/'))

    def primary_key_to_url(self):
        """

        Small helper method to obtain a url snipped for addressing a database resource by its primary key (it may be a
        composite one)
        The result is something like this: '/{primary_key_column_name_1:\d+}/{primary_key_column_name_1:\d+}'

        :return: the string representing the url snippet
        :rtype : str
        """
        sub_url = []
        for column_name in self.model.pk_column_names():
            sub_url.append('{' + column_name + ':\\d+}')
        return '/' + '/'.join(sub_url)

    def provide_session(self, request):
        """
        This method provides a usable SQLAlchemy session instance. It is ensured, that this session is doomed
        independent from the behavior of the request (it installs a finished listener to the request)


        :param request: The request of the pyramid web framework
        :type request: Request
        :return: a usable instance of a SQLAlchemy Session
        :rtype : Session
        """
        Session = sessionmaker(bind=self.engine)
        session_instance = Session()

        def cleanup(request):
            if request.exception is not None:
                print request.exception
                print 'rollback session because request error was thrown'
                session_instance.rollback()
            else:
                print 'commit session, everything is ok'
                session_instance.commit()
            session_instance.close()
        request.add_finished_callback(cleanup)

        return session_instance

    def read(self, request):
        """
        Read the records from the corresponding database table.

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: a dict where the database results are mapped to 'features' attribute as a list
        :rtype : dict of 'features': [Object]
        """
        session = self.provide_session(request)
        objects = session.query(self.model).all()
        return {'features': objects}

    def read_one(self, request):
        """

        Try to read exactly one record from database specified by the primary key

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: a dict where the database results are mapped to 'features' attribute as a list (contains exactly one)
        :rtype : dict of 'features': [Object] or HTTPNotFound
        :raises: HTTPNotFound
        """
        try:
            session = self.provide_session(request)
            query = session.query(self.model)
            for column_name in self.model.pk_column_names():
                pk_id = request.matchdict.get(column_name, None)
                query = query.filter(self.model.pk_columns().get(column_name) == pk_id)
                # return list because the renderer accepts list as input only
            return {'features': [query.one()]}
        except NoResultFound, e:
            print e
            text_list = []
            for column_name in self.model.pk_column_names():
                pk_id = request.matchdict.get(column_name, None)
                text_list.append('{0}: {1}'.format(column_name, str(pk_id)))
            text = ', '.join(text_list)
            raise HTTPNotFound(body_template=self.not_found_text.format(text))

    def count(self, request):
        """
        Count the records in the corresponding database table.

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: the number of found database records
        :rtype : int
        """
        session = self.provide_session(request)
        count = session.query(self.model).count()
        return count

    def description(self, request):
        """
        Describe the underling database table as a python dictionary

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: the number of found database records
        :rtype : dict
        """
        return self.model.description()

    def create(self, request):
        """
        Creates a new record in the corresponding database table.

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: a dict where the database results are mapped to 'features' attribute as a list (contains exactly one)
        :rtype : dict of 'features': [Object] or HTTPNotFound
        :raises: HTTPBadRequest or HTTPServerError
        """
        try:
            data = request.json_body.get('features')
            if data is None:
                raise HTTPBadRequest(body_template=self.bad_text)
            else:
                session = self.provide_session(request)
                new_record = self.model()
                for key, value in data.iteritems():
                    if key == 'geom':
                        value = WKBSpatialElement(buffer(wkt.loads(value).wkb), srid=2056)
                    setattr(new_record, key, value)
                session.add(new_record)
                session.flush()
                request.response.status_int = 201
                return {'features': [new_record]}
        except IntegrityError, e:
            print e
            raise HTTPServerError(detail='Integrity Error', body_template=self.integrity_error_txt)

    def update(self, request):
        """
        Updates a record in the corresponding database table.

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: a dict where the database results are mapped to 'features' attribute as a list (contains exactly one)
        :rtype : dict of 'features': [Object] or HTTPNotFound
        :raises: HTTPBadRequest or HTTPServerError
        """
        try:
            data = request.json_body.get('features')
            if data is None:
                raise HTTPBadRequest(body_template=self.bad_text)
            else:
                session = self.provide_session(request)
                query = session.query(self.model)
                for column_name in self.model.pk_column_names():
                    pk_id = request.matchdict.get(column_name, None)
                    query = query.filter(self.model.pk_columns().get(column_name) == pk_id)
                    # return list because the renderer accepts list as input only
                element = query.one()
                for key, value in data.iteritems():
                    if key == 'geom':
                        value = WKBSpatialElement(buffer(wkt.loads(value).wkb), srid=2056)
                    setattr(element, key, value)
                session.flush()
                request.response.status_int = 202
                return {'features': [element]}
        except NoResultFound, e:
            print e
            text_list = []
            for column_name in self.model.pk_column_names():
                pk_id = request.matchdict.get(column_name, None)
                text_list.append('{0}: {1}'.format(column_name, str(pk_id)))
            text = ', '.join(text_list)
            raise HTTPNotFound(body_template=self.not_found_text.format(text))

    def delete(self, request):
        """
        Deletes a record in the corresponding database table.

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: a dict where the database results are mapped to 'features' attribute as a list (contains exactly one)
        :rtype : dict of 'features': [Object] or HTTPNotFound
        :raises: HTTPBadRequest or HTTPServerError
        """
        try:
            data = request.json_body.get('features')
            if data is None:
                raise HTTPBadRequest(body_template=self.bad_text)
            else:
                session = self.provide_session(request)
                query = session.query(self.model)
                for column_name in self.model.pk_column_names():
                    pk_id = request.matchdict.get(column_name, None)
                    query = query.filter(self.model.pk_columns().get(column_name) == pk_id)
                    # return list because the renderer accepts list as input only
                element = query.one()
                session.delete(element)
                session.flush()
                request.response.status_int = 202
                return {'features': [element]}
        except NoResultFound, e:
            print e
            text_list = []
            for column_name in self.model.pk_column_names():
                pk_id = request.matchdict.get(column_name, None)
                text_list.append('{0}: {1}'.format(column_name, str(pk_id)))
            text = ', '.join(text_list)
            raise HTTPNotFound(body_template=self.not_found_text.format(text))