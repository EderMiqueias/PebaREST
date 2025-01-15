from pebarest.models.request import Request
from pebarest.models.response import Response
from pebarest.exceptions import MethodNotAllowedError
from pebarest.models.http import HttpMethods, http_methods_list


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
