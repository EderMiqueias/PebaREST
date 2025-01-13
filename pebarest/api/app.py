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

    def add_route(self, path: str, resource: object):
        if path in self.__routes:
            raise RouteAlreadyExistsError(path)
        self.__routes[path] = resource


class App:
    def __init__(self, manager=RoutesManager):
        self._routes_manager: RoutesManager = manager()

    def add_route(self, path: str, resource: object):
        self._routes_manager.add_route(path, resource)

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path in self._routes_manager:
            resource = self._routes_manager.routes[path]
            request = Request(environ)
            response = Response()

            if environ['REQUEST_METHOD'] == 'GET':
                resource.get(request)

            start_response(response.status, response.headers.items())
            return [response.body.encode('utf-8')]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Resoure not found']


class Request:
    def __init__(self, environ):
        self.method = environ['REQUEST_METHOD']
        self.path = environ['PATH_INFO']


class Response:
    def __init__(self):
        self.status = '200 OK'
        self.headers = {'Content-Type': 'application/json'}
        self.body = '{"message": "Bem-vindo!"}'
