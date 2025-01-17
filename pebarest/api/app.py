from typing import Union

from pebarest.models import Resource, Request
from pebarest.exceptions import RouteAlreadyExistsError


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


class App:
    def __init__(self, default_headers: dict=None, manager=RoutesManager):
        if default_headers is None:
            default_headers = {}

        self._routes_manager: RoutesManager = manager()
        self.headers = default_headers

    def add_route(self, path: str, resource: Union[object, Resource]):
        if isinstance(resource, Resource):
            if not resource.headers:
                resource.headers = self.headers
            self._routes_manager.add_route(path, resource)
        else:
            resource = Resource.from_anonymous_object(resource, self.headers)
            self._routes_manager.add_route(path, resource)

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path in self._routes_manager:
            resource = self._routes_manager.routes[path]
            request = Request(environ)

            response = resource(environ['REQUEST_METHOD'], request)
            start_response(response.get_status(), list(response.headers.items()))
            return response.get_body_bytes()
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Resource not found']
