import bisect
import typing as t
from functools import reduce
from horseman.types import WSGICallable, Environ, StartResponse


WSGIMiddleware = t.Callable[[WSGICallable], WSGICallable]


class Middlewares(WSGICallable):

    __slots__ = ('__call__', '_chain', 'wrapped')

    wrapped: WSGICallable
    _chain: t.List[WSGIMiddleware]

    def __init__(self, wrapped: WSGICallable):
        self.__call__ = self.wrapped = wrapped
        self._chain = []

    def update(self):
        if not self._chain:
            if self.__call__ and self.__call__ != self.wrapped:
                self.__call__ = self.wrapped
            return

        self.__call__ = reduce(
            lambda x, y: y(x),
            (m[1] for m in reversed(self._chain)),
            self.wrapped
        )

    def add(self, middleware: WSGIMiddleware, order: int = 0):
        if not self._chain:
            self._chain = [(order, middleware)]
        else:
            bisect.insort(self._chain, (order, middleware))
        self.update()

    def remove(self, middleware: WSGIMiddleware, order: int = 0):
        self._chain.remove((order, middleware))
        self.update()

    def clear(self):
        self._chain.clear()
        self.__call__ = self.wrapped

    def __iter__(self):
        return iter(self._chain)
