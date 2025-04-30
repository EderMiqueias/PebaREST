from typing import Union

from pebarest.models import Resource, Request, Response, DefaultErrorResponse
from pebarest.exceptions import RouteAlreadyExistsError, MethodNotAllowedError, NotFoundError


class RoutesManager:
    __routes: dict = {}

    def __init__(self, routes=None):
        if routes is None:
            routes = {}
        self.__routes = routes

    def __iter__(self):
        yield from self.__routes.keys()

    @property
    def routes(self):
        return self.__routes

    def add_route(self, path: str, resource: Resource):
        if path in self.__routes:
            raise RouteAlreadyExistsError(path)
        self.__routes[path] = resource

    def get_route_resource(self, path: str) -> Resource:
        try:
            return self.__routes[path]
        except KeyError:
            raise NotFoundError()


class App:
    def __init__(
            self,
            default_headers: dict=None,
            manager=RoutesManager,
            error_format=DefaultErrorResponse
    ):
        if default_headers is None:
            default_headers = {}

        self._routes_manager: RoutesManager = manager()
        self.headers = default_headers

        if not issubclass(error_format, dict):
            raise TypeError('The error format class must be a subclass of dict.')
        self.error_format=error_format

    def add_route(self, path: str, resource: Union[object, Resource]):
        if isinstance(resource, Resource):
            if not resource.headers:
                resource.headers = self.headers
            self._routes_manager.add_route(path, resource)
        else:
            resource = Resource.from_anonymous_object(resource, self.headers)
            self._routes_manager.add_route(path, resource)

    def __call__(self, environ: dict, start_response):
        try:
            resource = self._routes_manager.get_route_resource(environ['PATH_INFO'])
            response = resource(environ)
        except MethodNotAllowedError as e:
            response = Response(405, self.headers, self.error_format(e.title, method=e.method))
        except NotFoundError as e:
            response = Response(e.status_code, self.headers, self.error_format(e.message))
        except AttrTypeError as e:
            response = Response(422, self.headers, self.error_format.attr_type_error(e))
        except Exception as e:
            response = Response(500, self.headers, self.error_format('Internal Server Error'))

        start_response(response.get_status(), list(response.headers.items()))
        return response.get_body_bytes()
