# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


class Connection:

    def __init__(self, url):
        """
        Simple wrapper class to have all connection specific stuff in one simple accessible place.

        :param url: The connection string which is used to let the api connect with the desired database.
        It must have the form as described here:
        http://docs.sqlalchemy.org/en/latest/core/engines.html
        :type url: str
        """
        self.url = url
        if 'cx_oracle' in self.url:
            self.engine = create_engine(self.url, pool_size=1, coerce_to_unicode=True)
        else:
            self.engine = create_engine(self.url, pool_size=1)
        self.session = scoped_session(sessionmaker(bind=self.engine, extension=ZopeTransactionExtension()))
