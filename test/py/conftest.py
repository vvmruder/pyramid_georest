# -*- coding: utf-8 -*-

import pytest
from pyramid.testing import DummyRequest


class MockRequest(DummyRequest):
    def __init__(self, **kwargs):
        super(MockRequest, self).__init__(**kwargs)
        self.scheme = 'http'
        self.db_session = None
        self.environ = dict()
        self.set_application_url('http://localhost')
        self.host_url = 'http://localhost'
        self.route_prefix = 'test'

    def set_application_url(self, url):
        self.application_url = url


@pytest.fixture
def mock_request():
    return MockRequest()
