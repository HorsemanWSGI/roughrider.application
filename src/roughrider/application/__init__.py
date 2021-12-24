from typing import Optional
from dataclasses import dataclass, field
from horseman.types import Environ, WSGICallable
from roughrider.routing.route import NamedRoutes
from roughrider.routing.components import RoutingNode
from roughrider.application.request import Request


@dataclass
class Application(RoutingNode):
    routes: NamedRoutes = field(default_factory=dict)
    utilities: dict = field(default_factory=dict)
    request_factory: Type[Request] = Request

    def resolve(self, path: str, environ: Environ) -> Optional[WSGICallable]:
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            request = self.request_factory(self, environ, route)
            return route.endpoint(request, **route.params)