from typing import Optional, Type
from dataclasses import dataclass, field
from horseman.meta import Node
from horseman.types import Environ, WSGICallable, StartResponse
from roughrider.routing.components import NamedRoutes
from roughrider.application.request import Request
from roughrider.application.middleware import Middlewares


@dataclass
class Application(Node):
    routes: NamedRoutes = field(default_factory=NamedRoutes)
    utilities: dict = field(default_factory=dict)
    request_factory: Type[Request] = Request

    def resolve(self, path: str, environ: Environ) -> Optional[WSGICallable]:
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            request = self.request_factory(self, environ, route)
            return route.endpoint(request, **route.params)


@dataclass
class WrappableApplication(Application):
    middlewares: Middlewares = None

    def __post_init__(self):
        if self.middlewares is None:
            self.middlewares = Middlewares(super().__call__)

    def __call__(self, environ: Environ, start_response: StartResponse):
        return self.middlewares(environ, start_response)
