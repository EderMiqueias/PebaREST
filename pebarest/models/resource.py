from pebarest.models.request import Request
from pebarest.models.response import Response
from pebarest.exceptions import MethodNotAllowedError
from pebarest.models.http import HttpMethods


class Resource:
    _map_methods: dict
    headers: dict

    def __init__(self, default_headers: dict=None):
        self._map_methods = {
            'GET': self.get,
            'POST': self.post,
            'PUT': self.put,
            'PATCH': self.patch,
            'DELETE': self.delete,
            'HEAD': self.head,
            'OPTIONS': self.options
        }
        self.headers = default_headers or {}

    def __call__(self, method, request: Request, *args, **kwargs) -> Response:
        response, status_code = self._map_methods[method](request, *args, **kwargs)
        if type(response) == Response:
            return response
        if status_code:
            return Response(status_code, self.headers, response)
        return Response(200, self.headers, None)

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
