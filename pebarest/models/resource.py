from pebarest.models.response import Response
from pebarest.exceptions import MethodNotAllowedError
from pebarest.models.http import HttpMethods


class Resource:
    def get(self, request) -> Response:
        raise MethodNotAllowedError(HttpMethods.get)

    def post(self, request) -> Response:
        raise MethodNotAllowedError(HttpMethods.post)

    def put(self, request) -> Response:
        raise MethodNotAllowedError(HttpMethods.put)

    def patch(self, request) -> Response:
        raise MethodNotAllowedError(HttpMethods.patch)

    def delete(self, request) -> Response:
        raise MethodNotAllowedError(HttpMethods.delete)

    def head(self, request) -> Response:
        raise MethodNotAllowedError(HttpMethods.head)

    def options(self, request) -> Response:
        raise MethodNotAllowedError(HttpMethods.options)


__all__ = ['Resource']