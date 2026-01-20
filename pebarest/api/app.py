import logging

from typing import Union

from pebarest.models import Resource, Request, Response, DefaultErrorResponse
from pebarest.exceptions import RouteAlreadyExistsError, MethodNotAllowedError, NotFoundError, AttrMissingError, \
    AttrTypeError
from pebarest.utils.caching import CachedProperty
from pebarest.utils.logging import create_logger


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
            import_name: str,
            default_headers: dict=None,
            is_debug: bool=False,
            routes_manager=RoutesManager,
            error_format=DefaultErrorResponse
            # TODO: ADICIONAR UM STATUS_CODE_HANDLER DEFAULT POSSIBILITANDO AO USUARIO RETORNAR O STATUS CODE QUE ELE ACHAR MELHOR A DEPENDER DO TIPO DE ERRO
    ):
        if default_headers is None:
            default_headers = {}
        self.import_name = import_name
        self.is_debug = is_debug

        self._routes_manager: RoutesManager = routes_manager()
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

    @CachedProperty
    def logger(self) -> logging.Logger:
        return create_logger(self.import_name, self.is_debug)

    def __call__(self, environ: dict, start_response=None):
        try:
            resource = self._routes_manager.get_route_resource(environ['PATH_INFO'])
            response = resource(environ)
        except MethodNotAllowedError as e:
            response = Response(405, self.headers, self.error_format(e.title, method=e.method))
        except NotFoundError as e:
            response = Response(e.status_code, self.headers, self.error_format(e.message))
        except AttrMissingError as e:
            response = Response(422, self.headers, self.error_format.attr_missing_error(e))
        except AttrTypeError as e:
            response = Response(422, self.headers, self.error_format.attr_type_error(e))
        except Exception as e:
            self.logger.exception(e)
            response = Response(500, self.headers, self.error_format('Internal Server Error'))

        if response.status < 200:
            self.logger.info(str(response.body))
        if 300 >= response.status < 400:
            self.logger.warning(str(response.body))
        if 400 >= response.status < 500:
            self.logger.error(str(response.body))
        elif response.status >= 500:
            self.logger.critical(str(response.body))

        if start_response is not None:
            start_response(response.get_status(), list(response.headers.items()))
        return response.get_body_bytes()
