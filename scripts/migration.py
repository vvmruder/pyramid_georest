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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__author__ = 'Clemens Rudert'
__create_date__ = '23.07.2015'

_schema = 'webservices_v1'


def tutorial(create=False):
    from pyramid_rest.models import Webservice, Base

    engine1 = create_engine('postgresql://postgres:p1MJcc3$@localhost:5432/gdwh', echo=True)

    w = Webservice(name='test')

    if create:
        Base.metadata.drop_all(engine1)
        Base.metadata.create_all(engine1)
    webservice = Webservice(name='zweiter TEST')
    Session = sessionmaker(bind=engine1)
    session = Session()
    session.add_all([webservice, w])
    session.commit()

    class abc():
        service = w
        session = Session()

    return abc()