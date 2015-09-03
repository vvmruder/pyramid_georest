# # -*- coding: iso-8859-1 -*-
#
# # Copyright (c) 2012 - 2015, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
# # All rights reserved.
# #
# # This program is free software and completes the GeoMapFish License for the geoview.bl.ch specific
# # parts of the code. You can redistribute it and/or modify it under the terms of the GNU General
# # Public License as published by the Free Software Foundation, either version 3 of the License, or
# # (at your option) any later version.
# #
# # This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# # even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# # General Public License for more details.
# #
# # The above copyright notice and this permission notice shall be included in all copies or substantial
# # portions of the Software.
# import c2cgeoportal as c2c
#
# c2c.schema = 'main'
# c2c.srid = 2056
# from c2cgeoportal.models import Role
# from sqlalchemy.orm import sessionmaker, relation
# from sqlalchemy import create_engine, Column, types, event, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from pyramid_rest.lib.rest import Rest
# from pyramid_rest.models import Base
# import importlib
#
#
#
# __author__ = 'Clemens Rudert'
# __create_date__ = '23.07.2015'
#
# _schema = 'webservices_v1'
#
# engine = create_engine('postgresql://postgres:p1MJcc3$@localhost:5432/bl_gis2012', echo=True)
# Session = sessionmaker(bind=engine)
#
#
# class RestService(Base):
#     __tablename__ = 'rest_service'
#     __table_args__ = {'schema': 'main'}
#     id = Column(types.Integer, primary_key=True)
#     model = Column(types.Unicode, unique=True)
#     description_text = Column(types.Unicode)
#     name = Column(types.Unicode)
#     database_connection = Column(types.Unicode)
#     with_permission = Column(types.Boolean, default=False)
#
#
# class RestServiceRole(Base):
#     __tablename__ = 'rest_service_role'
#     __table_args__ = {'schema': 'main'}
#     id = Column(types.Integer, primary_key=True)
#     rest_service_id = Column(types.Integer, ForeignKey(RestService.id))
#     role_id = Column(types.Integer, ForeignKey(Role.id))
#     read_json = Column(types.Boolean, default=False)
#     read_xml = Column(types.Boolean, default=False)
#     read_html = Column(types.Boolean, default=False)
#     read_one_json = Column(types.Boolean, default=False)
#     read_one_xml = Column(types.Boolean, default=False)
#     read_one_html = Column(types.Boolean, default=False)
#     create = Column(types.Boolean, default=False)
#     update = Column(types.Boolean, default=False)
#     delete = Column(types.Boolean, default=False)
#     count = Column(types.Boolean, default=False)
#     model_json = Column(types.Boolean, default=False)
#     model_xml = Column(types.Boolean, default=False)
#     doc = Column(types.Boolean, default=False)
#
#
# def create_tables():
#     RestService.__table__.create(bind=engine)
#     RestServiceRole.__table__.create(bind=engine)
#
#
# def drop_tables():
#     RestService.__table__.drop(engine)
#     RestServiceRole.__table__.drop(engine)
#
#
# def create_record():
#     session_instance = Session()
#     rest_service_instance = RestService()
#     rest_service_instance.model = 'pyramid_rest.scripts.migration.RestService'
#     rest_service_instance.database_path = 'postgresql://postgres:p1MJcc3$@localhost:5432/bl_gis2012'
#     rest_service_instance.description_text = u'Das ist eine Beschreibung die üblicherweise korrekt ankommen sollte.'
#     rest_service_instance.name = 'Restful Webservice'
#     rest_service_instance.with_permission = True
#     session_instance.add(rest_service_instance)
#
#     session_instance.commit()
#     session_instance.close()
#
#
# def find_record(id_value):
#     session_instance = Session()
#     result = session_instance.query(RestService).filter(RestService.id == id_value).one()
#     session_instance.commit()
#     session_instance.close()
#     return result