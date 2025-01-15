from pebarest.models.request import Request
from pebarest.models.response import Response
from pebarest.exceptions import MethodNotAllowedError
from pebarest.models.http import HttpMethods


class Resource:
    _map_methods: dict

    def __init__(self):
        self._map_methods = {
            'GET': self.get,
            'POST': self.post,
            'PUT': self.put,
            'PATCH': self.patch,
            'DELETE': self.delete,
            'HEAD': self.head,
            'OPTIONS': self.options
        }

    def __call__(self, method, request: Request, *args, **kwargs):
        self._map_methods[method](request, *args, **kwargs)

    def get(self, request: Request, *args, **kwargs) -> Response:
        raise MethodNotAllowedError(HttpMethods.get)

    def post(self, request: Request, *args, **kwargs) -> Response:
        raise MethodNotAllowedError(HttpMethods.post)

    def put(self, request: Request, *args, **kwargs) -> Response:
        raise MethodNotAllowedError(HttpMethods.put)

    def patch(self, request: Request, *args, **kwargs) -> Response:
        raise MethodNotAllowedError(HttpMethods.patch)

    def delete(self, request: Request, *args, **kwargs) -> Response:
        raise MethodNotAllowedError(HttpMethods.delete)

    def head(self, request: Request, *args, **kwargs) -> Response:
        raise MethodNotAllowedError(HttpMethods.head)

    def options(self, request: Request, *args, **kwargs) -> Response:
        raise MethodNotAllowedError(HttpMethods.options)


__all__ = ['Resource']
