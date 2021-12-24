import typing as t
import urllib.parse
import horseman.parsers
import horseman.types
import horseman.http
import horseman.datastructures
from dataclasses import dataclass
from roughrider.routing.route import Route
from roughrider.routing.components import RoutingNode, RoutingRequest


class Request(RoutingRequest):

    __slots__ = (
        '_data',
        'app',
        'content_type',
        'cookies',
        'environ',
        'method',
        'query',
        'route',
        'script_name',
    )

    app: RoutingNode
    content_type: t.Optional[horseman.http.ContentType]
    cookies: horseman.http.Cookies
    environ: horseman.types.Environ
    method: horseman.types.HTTPMethod
    query: horseman.http.Query
    route: Route
    script_name: str

    _data: t.Optional[horseman.datastructures.FormData]

    def __init__(self,
                 app: RoutingNode,
                 environ: horseman.types.Environ,
                 route: Route):
        self._data = ...
        self.app = app
        self.environ = environ
        self.method = environ['REQUEST_METHOD'].upper()
        self.route = route
        self.query = horseman.http.Query.from_environ(environ)
        self.cookies = horseman.http.Cookies.from_environ(environ)
        self.script_name = urllib.parse.quote(environ['SCRIPT_NAME'])
        if 'CONTENT_TYPE' in self.environ:
            self.content_type = horseman.http.ContentType.from_http_header(
                self.environ['CONTENT_TYPE'])
        else:
            self.content_type = None

    def extract(self) -> horseman.datastructures.FormData:
        if self._data is not ...:
            return self._data()

        if self.content_type:
            self._data = horseman.parsers.parser(
                self.environ['wsgi.input'], self.content_type)

        return self._data

    def route_path(self, name, **params):
        if not self.app.routes.has_route(name):
            return None
        return self.script_name + self.app.routes.url_for(name, **params)

    def application_uri(self):
        scheme = self.environ['wsgi.url_scheme']
        http_host = self.environ.get('HTTP_HOST')
        if http_host:
            server, port = http_host.split(':', 1)
        else:
            server = self.environ['SERVER_NAME']
            port = self.environ['SERVER_PORT']

        if (scheme == 'http' and port == '80') or \
           (scheme == 'https' and port == '443'):
            return f'{scheme}://{server}{self.script_name}'
        return f'{scheme}://{server}:{port}{self.script_name}'

    def uri(self, include_query=True):
        url = self.application_uri()
        path_info = urllib.parse.quote(self.environ.get('PATH_INFO', ''))
        if include_query:
            qs = urllib.parse.quote(self.environ.get('QUERY_STRING'))
            if qs:
                return f"{url}{path_info}?{qs}"
        return f"{url}{path_info}"
