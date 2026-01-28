from typing import get_type_hints, get_args, Optional, Dict, Callable

from pebarest.models.request import Request
from pebarest.models.response import Response
from pebarest.exceptions import MethodNotAllowedError
from pebarest.models.http import HttpMethods, http_methods_list


class Resource:
    __map_methods: Dict[str, Callable]
    __method_body_type: Dict[str, Optional[type]]
    headers: Dict[str, str]

    def __init__(self, default_headers: Optional[Dict[str, str]] = None):
        self.__map_methods = {}
        self.__method_body_type = {}

        for method in http_methods_list:
            handler = getattr(self, method)
            self.__map_methods[method] = handler
            annotations = get_type_hints(handler)
            request_type = annotations.get('request')

            if request_type:
                args = get_args(request_type)
                self.__method_body_type[method] = args[0] if args else None
            else:
                self.__method_body_type[method] = None

        self.headers = default_headers or {}

    def __call__(self, environ, *args, **kwargs) -> Response:
        body_response, status_code = None, 200
        method = environ['REQUEST_METHOD']
        request = Request(environ, self.__method_body_type[method])
        call_return = self.__map_methods[method](request, *args, **kwargs)

        if isinstance(call_return, Response):
            return call_return
        if isinstance(call_return, (dict, str, int, float, bool, list)):
            body_response = call_return
        elif isinstance(call_return, tuple):
            if len(call_return) > 0:
                body_response = call_return[0]
                if len(call_return) > 1:
                    status_code = call_return[1]
        return Response(status_code, self.headers, body_response)

    @property
    def used_methods(self) -> Dict[str, Callable]:
        used_methods = {}
        for method, handler in self.__map_methods.items():
            if id(getattr(self.__class__, method)) != id(getattr(Resource, method)):
                used_methods[method] = handler
        return used_methods

    @property
    def method_body_type(self) -> Dict[str, Optional[type]]:
        return self.__method_body_type

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
