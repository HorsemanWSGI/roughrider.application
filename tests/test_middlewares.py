import pytest
import logging
import webtest.app
from horseman.response import Response
from roughrider.application import WrappableApplication


def auth_middleware(app):
    def auth_wrapping(environ, start_response):
        if environ.get('REMOTE_USER') == 'admin':
            return app(environ, start_response)
        return Response(401)(environ, start_response)
    return auth_wrapping


def log_middleware(app):
    def log_wrapping(environ, start_response):
        logging.getLogger().info('logged')
        return app(environ, start_response)
    return log_wrapping


def test_add_duplicate_middleware():
    app = WrappableApplication()
    app.middlewares.add(log_middleware, 10)
    app.middlewares.add(log_middleware, 10)
    assert list(app.middlewares) == [
        (10, log_middleware),
        (10, log_middleware),
    ]
    app.middlewares.remove(log_middleware, 10)
    assert list(app.middlewares) == [
        (10, log_middleware)
    ]


def test_add_remove_middleware():
    app = WrappableApplication()
    assert list(app.middlewares) == []
    app.middlewares.add(log_middleware, 20)
    app.middlewares.add(auth_middleware, 10)
    assert list(app.middlewares) == [
        (10, auth_middleware),
        (20, log_middleware),
    ]
    app.middlewares.add(log_middleware, 0)
    assert list(app.middlewares) == [
        (0, log_middleware),
        (10, auth_middleware),
        (20, log_middleware),
    ]

    app.middlewares.remove(auth_middleware, 10)
    assert list(app.middlewares) == [
        (0, log_middleware),
        (20, log_middleware),
    ]

    with pytest.raises(ValueError):
        app.middlewares.remove(auth_middleware, 10)

    app.middlewares.clear()
    assert list(app.middlewares) == []


def test_middleware_caller(caplog):
    app = WrappableApplication()

    @app.routes.register('/')
    def endpoint(request):
        return Response(200, body=b'Test')

    wsgi = webtest.app.TestApp(app)
    response = wsgi.get("/")
    assert response.body == b'Test'

    app.middlewares.add(auth_middleware, 10)
    response = wsgi.get("/", expect_errors=True)
    assert response.status == '401 Unauthorized'

    app.middlewares.add(log_middleware, 20)
    with caplog.at_level(logging.INFO):
        response = wsgi.get("/", expect_errors=True)
    assert response.status == '401 Unauthorized'

    with caplog.at_level(logging.INFO):
        response = wsgi.get("/", extra_environ={"REMOTE_USER": "admin"})
    assert response.body == b'Test'
    assert caplog.record_tuples == [('root', 20, 'logged')]
    caplog.clear()

    app.middlewares.remove(auth_middleware, 10)
    with caplog.at_level(logging.INFO):
        response = wsgi.get("/")
    assert response.status == '200 OK'
    assert caplog.record_tuples == [('root', 20, 'logged')]
    caplog.clear()

    app.middlewares.remove(log_middleware, 20)
    with caplog.at_level(logging.INFO):
        response = wsgi.get("/")
    assert response.status == '200 OK'
    assert caplog.record_tuples == []
