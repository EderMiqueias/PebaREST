from typing import get_type_hints, get_args, Optional, Dict, Callable

from pebarest.models.request import Request
from pebarest.models.response import Response
from pebarest.exceptions import MethodNotAllowedError
from pebarest.models.http import HttpMethods, http_methods_list


class Resource:
    _map_methods: Dict[str, Callable]
    headers: Dict[str, str]

    def __init__(self, default_headers: Optional[Dict[str, str]] = None):
        self._map_methods = {}

        for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']:
            handler = getattr(self, method.lower(), None)
            if handler:
                self._map_methods[method] = handler

        self.headers = default_headers or {}

    def __call__(self, method, request: Request, *args, **kwargs) -> Response:
        body_response, status_code = None, 200
        call_return = self._map_methods[method](request, *args, **kwargs)
        if type(call_return) == Response:
            return call_return
        if type(call_return) == dict:
            body_response = call_return
        elif type(call_return) == tuple:
            if len(call_return) > 0:
                body_response = call_return[0]
                if len(call_return) > 1:
                    status_code = call_return[1]
        return Response(status_code, self.headers, body_response)

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

    @classmethod
    def from_anonymous_object(cls, anonymous_object: object, default_headers: dict=None):
        if default_headers is None:
            default_headers = {}
        resource_cls = cls(default_headers)

        for method_name in http_methods_list:
            if hasattr(anonymous_object, method_name):
                setattr(resource_cls, method_name, getattr(anonymous_object, method_name))
        return resource_cls


def get_http_methods_attrs(cls):
    return list(filter(lambda attr: attr in http_methods_list, dir(cls)))


# Decorator to transform a simple class into a Resource
def resource(cls_custom_resource: type) -> type:
    cls_resource = Resource
    for method in get_http_methods_attrs(cls_custom_resource):
        setattr(cls_resource, method, getattr(cls_custom_resource, method))
    return cls_resource



__all__ = ['Resource', 'resource']
