import pytest
from horseman.http import HTTPError
from horseman.response import Response
from roughrider.application import Application
from roughrider.routing.components import NamedRoutes
from roughrider.application.request import Request


def test_application_defaults():
    app = Application()
    assert isinstance(app.routes, NamedRoutes)
    assert app.utilities == {}
    assert app.request_factory is Request

    app = Application(utilities={'emailer': 1})
    assert app.utilities == {'emailer': 1}


def test_application_resolver():
    app = Application()

    @app.routes.register('/test')
    def endpoint(request):
        return Response(200, body=b'Test')

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
    }
    response = app.resolve('/', environ)
    assert response is None

    response = app.resolve('/test', environ)
    assert response is not None
    assert isinstance(response, Response)
    assert response.body == b'Test'

    environ['REQUEST_METHOD'] = 'POST'
    with pytest.raises(HTTPError) as exc:
        app.resolve('/test', environ)

    assert str(exc.value) == 'HTTPStatus.METHOD_NOT_ALLOWED'
