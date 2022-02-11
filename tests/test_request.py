import pytest
import webtest.app
from io import BytesIO
from horseman.parsers import Data
from roughrider.application import Application
from roughrider.application.request import Request


def test_request_defaults():
    app = Application()
    environ = webtest.app.TestRequest.blank('/test', method='GET').environ
    request = Request(app, environ)
    assert request.method == 'GET'
    assert request.script_name == ''
    assert request.query == {}
    assert request.cookies == {}
    assert request.content_type == None
    assert request.application_uri == 'http://localhost'
    assert request.uri() == 'http://localhost/test'


def test_request_queryvars():
    app = Application()
    environ = webtest.app.TestRequest.blank(
        '/test?foo=1&bar=2', method='GET').environ
    request = Request(app, environ)
    assert request.query == {'bar': ['2'], 'foo': ['1']}
    assert request.query.to_dict() == {'bar': '2', 'foo': '1'}
    assert request.uri() == 'http://localhost/test?foo%3D1%26bar%3D2'
    assert request.uri(include_query=False) == 'http://localhost/test'


def test_request_uri():
    environ = {
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': '',
        'PATH_INFO': '/',
        'QUERY_STRING': '',
        'SERVER_NAME': 'test_domain.com',
        'SERVER_PORT': '80',
        'HTTP_HOST': 'test_domain.com:80',
        'SERVER_PROTOCOL': 'HTTP/1.0',
        'wsgi.url_scheme': 'http',
        'CONTENT_TYPE': "application/json",
        'QUERY_STRING': 'action=login&token=abcdef',
        'wsgi.input': BytesIO(
            b'''{"username": "test", "password": "test"}'''
        ),
        'wsgi.errors': BytesIO()
    }

    app = Application()
    request = Request(app, environ)
    assert request.uri() == (
        'http://test_domain.com/?action%3Dlogin%26token%3Dabcdef'
    )
    assert request.uri(include_query=False) == 'http://test_domain.com/'

    environ['SCRIPT_NAME'] = '/api'
    request = Request(app, environ)
    assert request.uri() == (
        'http://test_domain.com/api/?action%3Dlogin%26token%3Dabcdef'
    )
    assert request.uri(include_query=False) == 'http://test_domain.com/api/'

    environ['wsgi.url_scheme'] = 'https'
    environ['HTTP_HOST'] = 'example.com:443'
    environ['SERVER_PORT'] = '443'
    request = Request(app, environ)
    assert request.uri() == (
        'https://example.com/api/?action%3Dlogin%26token%3Dabcdef'
    )
    assert request.uri(include_query=False) == 'https://example.com/api/'

    environ['HTTP_HOST'] = 'example.com:999'
    environ['SERVER_PORT'] = '999'
    request = Request(app, environ)
    assert request.uri() == (
        'https://example.com:999/api/?action%3Dlogin%26token%3Dabcdef'
    )
    assert request.uri(include_query=False) == 'https://example.com:999/api/'

    environ['wsgi.url_scheme'] = 'http'
    request = Request(app, environ)
    assert request.uri() == (
        'http://example.com:999/api/?action%3Dlogin%26token%3Dabcdef'
    )
    assert request.uri(include_query=False) == 'http://example.com:999/api/'


def test_request_cookies():
    app = Application()
    environ = webtest.app.TestRequest.blank(
        '/test', cookies={'key': 'value'}).environ
    request = Request(app, environ)
    assert request.cookies == {'key': 'value'}


def test_request_data():
    environ = {
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': '',
        'PATH_INFO': '/',
        'QUERY_STRING': '',
        'SERVER_NAME': 'test_domain.com',
        'SERVER_PORT': '80',
        'HTTP_HOST': 'test_domain.com:80',
        'SERVER_PROTOCOL': 'HTTP/1.0',
        'wsgi.url_scheme': 'http',
        'CONTENT_TYPE': "application/json",
        'QUERY_STRING': 'action=login&token=abcdef',
        'wsgi.input': BytesIO(
            b'''{"username": "test", "password": "test"}'''
        ),
        'wsgi.errors': BytesIO()
    }
    app = Application()
    request = Request(app, environ)
    data = request.extract()

    assert data == Data(
        form=None,
        files=None,
        json={'username': 'test', 'password': 'test'}
    )

    assert request.extract() is data
