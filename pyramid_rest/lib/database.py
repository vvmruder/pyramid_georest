# -*- coding: iso-8859-1 -*-

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
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

__author__ = 'vvmruder'
__create_date__ = '08.09.16'


class Connection:

    def __init__(self, url):
        self.url = url
        if 'cx_oracle' in self.url:
            self.engine = create_engine(self.url, echo=True, pool_size=1, coerce_to_unicode=True)
        else:
            self.engine = create_engine(self.url, echo=True, pool_size=1)
        self.session = scoped_session(sessionmaker(bind=self.engine, extension=ZopeTransactionExtension()))