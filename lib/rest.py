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
import json
from geoalchemy import WKBSpatialElement
from pyramid_rest.lib.filter import Filter
from shapely import wkt
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest, HTTPServerError, HTTPUnauthorized
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from pyramid.config import Configurator
from pyramid.request import Request

__author__ = 'Clemens Rudert'
__create_date__ = '29.07.2015'


class Config(dict):

    def __init__(self, config, **kwargs):
        """

        :param config:
        :param kwargs:
        """
        super(Config, self).__init__(**kwargs)
        for key, value in config:
            setattr(self, key, value)


class Rest(object):
    """
    Offers an interface to make SQLAlchemy objects restful in a pyramids web framework way
    """
    not_found_text = u'No element was found in database, with primary key: ({0})'
    bad_text = u'You submitted data which is incorrect. Please check the shipped parameter of your request.'
    integrity_error_txt = u'Your submitted data was corrupt. This usually means your data hurts some database ' \
                          u'constrains'

    def __init__(self, database_connection, model, description_text=u'', name=u'', with_read_permission=False,
                 with_write_permission=False, debug=False, outer_use=False, dictionary=None):
        """

        Creates an object which handles all things to do to provide an rest interface for the passed model. Please note
        that the object which is created represents an service. This service must be bound to an pyramid apps
        configurator see the bind() method at this class.

        Please refer to the README.rst of this package to learn more about the usage.

        :param database_connection: A sqlalchemy compatible string. It is used to build an engine (see:
        http://docs.sqlalchemy.org/en/latest/core/engines.html).
        :type database_connection: str
        :param model: The mapper representing the database table, this must be an child class of the Base defined in
        .models!
        :type model: Base
        :param description_text: A description of the resource. It will be used for the automatic generated
        documentation.
        :type description_text: unicode
        :param name: The spoken and shown Name of the resource. It will be used for the automatic generated
        documentation.
        :type name: unicode
        :param with_permission: With this parameter you can decide, if this service is under authorisation or not. It is
         very important to know how this works. So keep tuned and read on: This Package is an addition to the wonderful
         Python WebFrameWork pyramid. So it is not that far, to not reinvent the wheel for restrict access to resources
         which are provided by this package. Because the only thing this package does, is to offer some URLs to access
         database resources. Pyramid has a very well developed way of restricting access to specific URLs. So we will
         use this mechanism to achieve it.

         Once you have set this parameter to true, all services are closed. They check if the asking has permission via
         the pyramid way. Each URL will be created with an permission named as follows (they should be self explaining):
         - read_json
         - read_xml
         - read_html
         - read_one_json
         - read_one_xml
         - read_one_html
         - create_one
         - update_one
         - delete_one
         - count
         - model_json
         - model_xml
         - doc
         Since we do it this way, it is all up to you decide in your own pyramid application and in the resource (model)
         of cause who can access what. The only thing you have to do is to define your model right. It could be as
         follows:

         class Blog(object):
            def __acl__(self):
                return [
                    (Allow, Everyone, 'read_json'),
                    (Allow, self.owner, 'create'),
                    (Allow, 'group:editors', 'model_json'),
                ]

            def __init__(self, owner):
                self.owner = owner
        This gives you full power. Use it.
        :type with_read_permission: bool
        :param with_write_permission: see with_read_permission for explanation
        :type with_read_permission: bool
        :param debug: Turn on, to see a more detailed information in the log.
        :type debug: bool
        :param outer_use: Switch to configure if this resource is a common available one or not
        :type outer_use: bool
        :param dictionary: The pythonic path to a lookup like: '<package_name>:lang/dict.yaml'.
        :type dictionary: str
        """
        self.route_prefix = ''
        self.dictionary = dictionary
        self.outer_use = outer_use
        self.engine = scoped_session(create_engine(database_connection, echo=debug, pool_size=1))
        self.database_connection = database_connection
        self.model = model
        self.path = model.database_path().replace('.', '/')
        self.route_path = '/' + self.path
        self.with_read_permission = with_read_permission
        self.with_write_permission = with_write_permission
        self.name = name
        self.description_text = description_text
        self.outer_use = outer_use
        self.config = None
        self.session = sessionmaker(bind=self.engine)

    def bind(self, config):
        from pyramid_rest import _CREATE, _DELETE, _READ, _UPDATE
        """
        The bind method is the point, where all views and routes (URL-Resources) will be created. It is called from
        the includeme method of this package. You can call it manually of cause if you don't use this package via the
        pyramid extension way.
        :param config: The Configurator of the underling pyramid web app
        :type config: Configurator
        """

        self.route_prefix = config.route_prefix

        # set the route prefix to an empty string and handle prefix in the service itself. This prevents urls like
        # url/route_prefix/route_prefix/ressource.json ...
        config.route_prefix = ''

        # add the prefix to the path to have the full url path and to have the uri route name
        self.path = self.route_prefix + self.route_path

        self.config = {
            'name': self.name,
            'description': self.description_text,
            'path': self.path,
            'urls': {
                'read_json': self.path + '/read.json',
                'read_xml': self.path + '/read.xml',
                'read_html': self.path + '/read',
                'read_one_json': self.path + '/read' + self.primary_key_to_path() + '.json',
                'read_one_xml': self.path + '/read' + self.primary_key_to_path() + '.xml',
                'read_one_html': self.path + '/read' + self.primary_key_to_path(),
                'count': self.path + '/count',
                'model_json': self.path + '/model.json',
                'model_xml': self.path + '/model.xml',
                'doc': self.path if self.outer_use else '',
                'filter_provider_json': self.path + '/filter_provider.json',
                'filter_provider_xml': self.path + '/filter_provider.xml',
                'filter_provider_html': self.path + '/filter_provider.html',
                'fkey_provider_json': self.path + '/fkey_provider.json',
                'fkey_provider_xml': self.path + '/fkey_provider.xml',
                'fkey_provider_html': self.path + '/fkey_provider.html',
                'create_one': self.path + '/create',
                'update_one': self.path + '/update' + self.primary_key_to_path(),
                'delete_one': self.path + '/delete' + self.primary_key_to_path()
            }
        }

        config.add_route(
            self.config.get('urls').get('read_json'),
            self.config.get('urls').get('read_json')
        )
        config.add_view(
            self.read,
            renderer='restful_json',
            route_name=self.config.get('urls').get('read_json'),
            request_method=_READ,
            permission='read_json' if self.with_read_permission else None
        )

        config.add_route(
            self.config.get('urls').get('read_xml'),
            self.config.get('urls').get('read_xml')
        )
        config.add_view(
            self.read,
            renderer='restful_xml',
            route_name=self.config.get('urls').get('read_xml'),
            request_method=_READ,
            permission='read_xml' if self.with_read_permission else None
        )

        config.add_route(
            self.config.get('urls').get('read_one_json'),
            '/' + self.path + '/read' + self.primary_key_to_url() + '.json'
        )
        config.add_view(
            self.read_one,
            renderer='restful_json',
            route_name=self.config.get('urls').get('read_one_json'),
            request_method=_READ,
            permission='read_one_json' if self.with_read_permission else None
        )

        config.add_route(
            self.config.get('urls').get('read_one_xml'),
            '/' + self.path + '/read' + self.primary_key_to_url() + '.xml'
        )
        config.add_view(
            self.read_one,
            renderer='restful_xml',
            route_name=self.config.get('urls').get('read_one_xml'),
            request_method=_READ,
            permission='read_one_xml' if self.with_read_permission else None
        )

        config.add_route(
            self.config.get('urls').get('create_one'),
            self.config.get('urls').get('create_one')
        )
        config.add_view(
            self.create,
            renderer='restful_json',
            route_name=self.config.get('urls').get('create_one'),
            request_method=_CREATE,
            permission='create_one' if self.with_write_permission else None
        )

        config.add_route(
            self.config.get('urls').get('update_one'),
            '/' + self.path + '/update' + self.primary_key_to_url()
        )
        config.add_view(
            self.update,
            renderer='restful_json',
            route_name=self.config.get('urls').get('update_one'),
            request_method=_UPDATE,
            permission='update_one' if self.with_write_permission else None
        )

        config.add_route(
            self.config.get('urls').get('delete_one'),
            '/' + self.path + '/delete' + self.primary_key_to_url()
        )
        config.add_view(
            self.delete,
            renderer='restful_json',
            route_name=self.config.get('urls').get('delete_one'),
            request_method=_DELETE,
            permission='delete_one' if self.with_write_permission else None
        )

        config.add_route(
            self.config.get('urls').get('count'),
            self.config.get('urls').get('count')
        )
        config.add_view(
            self.count,
            renderer='jsonp',
            route_name=self.config.get('urls').get('count'),
            request_method=_READ,
            permission='count' if self.with_read_permission else None
        )

        config.add_route(
            self.config.get('urls').get('model_json'),
            self.config.get('urls').get('model_json')
        )
        config.add_view(
            self.description,
            renderer='model_restful_json',
            route_name=self.config.get('urls').get('model_json'),
            request_method=_READ,
            permission='model_json' if self.with_read_permission else None
        )

        config.add_route(
            self.config.get('urls').get('model_xml'),
            self.config.get('urls').get('model_xml')
        )
        config.add_view(
            self.description,
            renderer='model_restful_xml',
            route_name=self.config.get('urls').get('model_xml'),
            request_method=_READ,
            permission='model_xml' if self.with_read_permission else None
        )

        config.add_route(
            self.config.get('urls').get('read_html'),
            self.config.get('urls').get('read_html')
        )
        config.add_view(
            self.read,
            renderer='pyramid_rest:templates/read.mako',
            route_name=self.config.get('urls').get('read_html'),
            request_method=_READ,
            permission='read_html' if self.with_read_permission else None
        )

        config.add_route(
            self.config.get('urls').get('read_one_html'),
            '/' + self.path + '/read' + self.primary_key_to_url()
        )
        config.add_view(
            self.read_one,
            renderer='pyramid_rest:templates/read_one.mako',
            route_name=self.config.get('urls').get('read_one_html'),
            request_method=_READ,
            permission='read_one_html' if self.with_read_permission else None
        )
        config.add_route(
            self.config.get('urls').get('filter_provider_json'),
            self.config.get('urls').get('filter_provider_json')
        )
        config.add_view(
            self.filter_values,
            renderer='restful_json',
            route_name=self.config.get('urls').get('filter_provider_json'),
            request_method=_READ,
            permission='filter_provider_json' if self.with_read_permission else None
        )
        config.add_route(
            self.config.get('urls').get('filter_provider_xml'),
            self.config.get('urls').get('filter_provider_xml')
        )
        config.add_view(
            self.filter_values,
            renderer='restful_xml',
            route_name=self.config.get('urls').get('filter_provider_xml'),
            request_method=_READ,
            permission='filter_provider_xml' if self.with_read_permission else None
        )
        config.add_route(
            self.config.get('urls').get('filter_provider_html'),
            self.config.get('urls').get('filter_provider_html')
        )
        config.add_view(
            self.filter_values,
            renderer='pyramid_rest:templates/read.mako',
            route_name=self.config.get('urls').get('filter_provider_html'),
            request_method=_READ,
            permission='filter_provider_html' if self.with_read_permission else None
        )
        config.add_route(
            self.config.get('urls').get('fkey_provider_json'),
            self.config.get('urls').get('fkey_provider_json')
        )
        config.add_view(
            self.foreign_key_values,
            renderer='restful_json',
            route_name=self.config.get('urls').get('fkey_provider_json'),
            request_method=_READ,
            permission='fkey_provider_json' if self.with_read_permission else None
        )
        config.add_route(
            self.config.get('urls').get('fkey_provider_xml'),
            self.config.get('urls').get('fkey_provider_xml')
        )
        config.add_view(
            self.foreign_key_values,
            renderer='restful_xml',
            route_name=self.config.get('urls').get('fkey_provider_xml'),
            request_method=_READ,
            permission='fkey_provider_xml' if self.with_read_permission else None
        )
        config.add_route(
            self.config.get('urls').get('fkey_provider_html'),
            self.config.get('urls').get('fkey_provider_html')
        )
        config.add_view(
            self.foreign_key_values,
            renderer='pyramid_rest:templates/read.mako',
            route_name=self.config.get('urls').get('fkey_provider_html'),
            request_method=_READ,
            permission='fkey_provider_html' if self.with_read_permission else None
        )
        # create doc url only for services which are intended to be used as external api
        if self.outer_use:
            config.add_route(
                self.config.get('urls').get('doc'),
                self.config.get('urls').get('doc')
            )
            config.add_view(
                self.doc,
                renderer='pyramid_rest:templates/doc_specific.mako',
                route_name=self.config.get('urls').get('doc'),
                request_method=_READ,
                permission='doc' if self.with_read_permission else None
            )
        # Add the Webservice Object to the registry, so it can be addressed for meta_info in the main doc
        config.registry.pyramid_rest_services.append(self)

        # reset the route prefix to guarantee proper handling on further route_prefix use
        config.route_prefix = self.route_prefix

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

    def primary_key_to_path(self):
        """

        Small helper method to obtain a path snipped for addressing a database resource by its primary key (it may be a
        composite one)
        The result is something like this: '/primary_key_column_name_1/primary_key_column_name_1'

        :return: the string representing the url snippet
        :rtype : str
        """
        sub_url = []
        for column_name in self.model.pk_column_names():
            sub_url.append(column_name)
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
        session_instance = self.session()

        def cleanup(request):
            print 'clean up method was called !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            if request.exception is not None:
                # print request.exception
                # print 'rollback session because request error was thrown'
                session_instance.rollback()
            else:
                # print 'commit session, everything is ok'
                session_instance.commit()
            session_instance.remove()
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
        filter_definition = request.params.get('filter', default=None)
        if filter_definition is not None:
            try:
                filter_dict = json.loads(filter_definition)
                filter_instance = Filter(filter_dict, self.model, session)
                objects = filter_instance.do_filter().all()
                return {'features': objects}
            except ValueError, e:
                print e
                print 'filter definition: ', filter_definition
                raise HTTPBadRequest(body_template=self.bad_text)
        else:
            try:
                objects = session.query(self.model).all()
                return {'features': objects}
            except DatabaseError, e:
                print e
                print 'used connection: ', self.database_connection
                raise HTTPServerError()

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
        except DatabaseError, e:
                print e
                print 'used connection: ', self.database_connection
                raise HTTPServerError()

    def count(self, request):
        """
        Count the records in the corresponding database table.

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: the number of found database records
        :rtype : int
        """
        session = self.provide_session(request)
        filter_definition = request.params.get('filter', default=None)
        if filter_definition is not None:
            try:
                filter_dict = json.loads(filter_definition)
                filter_instance = Filter(filter_dict, self.model, session)
                count = filter_instance.do_filter().count()
                return count
            except ValueError, e:
                print e
                print 'filter definition: ', filter_definition
                raise HTTPBadRequest(body_template=self.bad_text)
        else:
            try:
                count = session.query(self.model).count()
                return count
            except DatabaseError, e:
                print e
                print 'used connection: ', self.database_connection
                raise HTTPServerError()

    def description(self, request):
        """
        Describe the underling database table as a python dictionary

        :param request: The request of the pyramid web framework
        :type request: Request
        :return: the number of found database records
        :rtype : dict
        """
        return self.model.description(self.dictionary)

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
        except DatabaseError, e:
                print e
                print 'used connection: ', self.database_connection
                raise HTTPServerError()

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
        except DatabaseError, e:
                print e
                print 'used connection: ', self.database_connection
                raise HTTPServerError()

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
        except DatabaseError, e:
                print e
                print 'used connection: ', self.database_connection
                raise HTTPServerError()

    def doc(self, request):
        return self.config

    def filter_values(self, request):
        try:
            if request.params.get('filter_column') is None:
                return HTTPBadRequest(body_template=self.bad_text)
            else:
                filter_column = request.params.get('filter_column')
            if request.params.get('limit') is None:
                limit = 20
            else:
                limit = request.params.get('limit')
            filter_definition = request.params.get('filter', default=None)
            if filter_definition is not None:
                session = self.provide_session(request)
                filter_instance = Filter(json.loads(filter_definition), self.model, session)
                filter_query = filter_instance.do_filter()
                query = filter_query.limit(limit)
                if len(filter_instance.filter_list) == 0 and len(filter_instance.filter_list_and) == 0 and len(
                        filter_instance.filter_list_or) == 0:
                    print 'Leerer Filter bei Filterwerten'
                    raise HTTPServerError()
                else:
                    column = getattr(self.model, filter_column)
                    objects = query.distinct(column).all()
                    return {'features': objects}
        except DatabaseError, e:
                print e
                print 'used connection: ', self.database_connection
                raise HTTPServerError()

    def foreign_key_values(self, request):
        try:
            if request.params.get('limit') is None:
                limit = 20
            else:
                limit = request.params.get('limit')
            filter_definition = request.params.get('filter', default=None)
            session = self.provide_session(request)
            if filter_definition is None:
                query = session.query(self.model)
                query = query.limit(limit)
            else:
                filter_query = Filter(json.loads(filter_definition), self.model, session)
                filter_query.do_filter()
                query = filter_query.query.limit(limit)
            for column_name in self.model.pk_column_names():
                query = query.distinct(self.model.pk_columns().get(column_name))
            return {'features': query.all()}
        except DatabaseError, e:
                print e
                print 'used connection: ', self.database_connection
                raise HTTPServerError()