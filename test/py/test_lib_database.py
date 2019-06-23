# -*- coding: utf-8 -*-
from sqlalchemy.engine import Engine
from pyramid_georest.lib.database import Connection
from sqlalchemy.orm.session import Session


def test_init():
    url = 'sqlite://'
    c = Connection(url)
    assert isinstance(c, Connection)
    assert c.url == url
    assert isinstance(c.session(), Session)
    assert isinstance(c.engine, Engine)
