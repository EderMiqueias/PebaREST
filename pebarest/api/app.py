import logging
import re

from typing import Dict, List, Optional, Tuple, Type, Union, Any

from pebarest import BaseModel
from pebarest.auth import BaseAuthenticator
from pebarest.models import Resource, Response, DefaultErrorResponse
from pebarest.exceptions import RouteAlreadyExistsError, MethodNotAllowedError, NotFoundError, AttrMissingError, \
    AttrTypeError
from pebarest.models.response import ErrorResponse
from pebarest.testing import UnitTestGenerator
from pebarest.testing.base_test_generator import TestGenerator
from pebarest.testing.test_client import TestClient
from pebarest.utils.caching import CachedProperty
from pebarest.utils.logging import create_logger


_PARAM_RE = re.compile(r'\{(\w+)\}')


class RoutesManager:
    __routes: Dict[str, Resource]
    __dynamic_routes: List[Tuple[re.Pattern, Resource]]

    def __init__(self, routes=None):
        self.__routes = routes if routes is not None else {}
        self.__dynamic_routes = []

    def __iter__(self):
        yield from self.__routes.keys()
        for pattern, _ in self.__dynamic_routes:
            yield pattern.pattern

    @property
    def routes(self) -> Dict[str, Resource]:
        return self.__routes

    @staticmethod
    def _compile_path(path: str) -> Optional[re.Pattern]:
        """Convert a path template like /users/{id} into a compiled regex."""
        if not _PARAM_RE.search(path):
            return None
        regex = _PARAM_RE.sub(r'(?P<\1>[^/]+)', path)
        return re.compile(f'^{regex}$')

    def add_route(self, path: str, resource: Resource):
        pattern = self._compile_path(path)
        if pattern is not None:
            for existing_pattern, _ in self.__dynamic_routes:
                if existing_pattern.pattern == pattern.pattern:
                    raise RouteAlreadyExistsError(path)
            self.__dynamic_routes.append((pattern, resource))
        else:
            if path in self.__routes:
                raise RouteAlreadyExistsError(path)
            self.__routes[path] = resource

    def get_route_resource(self, path: str) -> Resource:
        """Exact-match lookup. Kept for backwards compatibility."""
        try:
            return self.__routes[path]
        except KeyError:
            raise NotFoundError()

    def match_route(self, path: str) -> Tuple[Resource, Dict[str, str]]:
        """Return (resource, path_params) for the given request path."""
        # 1. Fast exact-match on static routes
        if path in self.__routes:
            return self.__routes[path], {}
        # 2. Linear scan over dynamic routes in registration order
        for pattern, resource in self.__dynamic_routes:
            match = pattern.fullmatch(path)
            if match:
                return resource, match.groupdict()
        raise NotFoundError()


class App:
    error_format: Type[ErrorResponse]
    import_name: str
    default_headers: dict
    is_debug: bool
    testing_generator: TestGenerator
    auth_handler: BaseAuthenticator
    
    def __init__(
            self,
            import_name: str,
            default_headers: dict=None,
            is_debug: bool=True,
            generate_docs: bool=False,
            auth_handler=None,
            routes_manager=RoutesManager,
            error_format=DefaultErrorResponse,
            testing_generator=UnitTestGenerator
            # TODO: ADICIONAR UM STATUS_CODE_HANDLER DEFAULT POSSIBILITANDO AO USUARIO RETORNAR O STATUS CODE QUE ELE ACHAR MELHOR A DEPENDER DO TIPO DE ERRO
    ):
        if default_headers is None:
            default_headers = {}
        self.import_name = import_name
        self.is_debug = is_debug
        self.generate_docs = generate_docs

        self.auth_handler = auth_handler
        self.routes_manager: RoutesManager = routes_manager()
        self.headers = default_headers

        if not issubclass(error_format, dict):
            raise TypeError('The error format class must be a subclass of dict.')
        self.error_format=error_format
        self.testing_generator = testing_generator(self)
        self.__tests_generated = False

    def add_route(self, path: str, resource: Union[object, Resource]):
        if isinstance(resource, Resource):
            if not resource.auth_handler:
                resource.auth_handler = self.auth_handler
            if not resource.headers:
                resource.headers = self.headers
            self.routes_manager.add_route(path, resource)
        else:
            resource = Resource.from_anonymous_object(resource, self.headers)
            self.add_route(path, resource)
    
    def generate_tests(self, test_cases: Dict[str, Dict[str, any]] = None, output_file=None):
        if self.is_debug:
            if self.testing_generator:
                self.testing_generator.generate(test_cases, output_file)
                self.__tests_generated = True

    @CachedProperty
    def _generate_openapi_json(self) -> Dict[str, Any]:
        """
        Scan the registered routes and build the OpenAPI 3.1.0 document.
        """
        paths = {}
        schemas = {}

        for path, resource in self.routes_manager.routes.items():
            path_item = {}
            for method_name, method_func in resource.used_methods.items():
                # TODO: ADICIONAR SUPORTE PARA RESPONSE MODELS E PARA DESCRIÇÃO DAS OPERAÇÕES
                operation = {
                    "responses": {
                        "200": {"description": "Sucesso"}
                    }
                }

                body_type = resource.method_body_type.get(method_name)
                if body_type and issubclass(body_type, BaseModel):
                    model_name = body_type.__name__
                    if model_name not in schemas:
                        schemas[model_name] = body_type.get_openapi_schema()

                    operation["requestBody"] = {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{model_name}"}
                            }
                        }
                    }

                path_item[method_name] = operation

            paths[path] = path_item

        return {
            "openapi": "3.1.0",
            "info": {
                "title": f"API {self.import_name}",
                "version": "1.0.0",
                "description": "Documentação gerada automaticamente pelo PebaREST"
            },
            "paths": paths,
            "components": {
                "schemas": schemas
            }
        }

    @CachedProperty
    def logger(self) -> logging.Logger:
        return create_logger(self.import_name, self.is_debug)

    def test_client(self):
        return TestClient(self)

    def __call__(self, environ: dict, start_response=None):
        if not self.__tests_generated:
            self.generate_tests()
        try:
            path = environ.get('PATH_INFO', '/')

            if self.generate_docs and path == '/docs':
                openapi_data = self._generate_openapi_json
                response = Response(200, self.headers, openapi_data)
                if start_response:
                    start_response(response.get_status(), list(response.headers.items()))
                return response.get_body_bytes()

            resource, path_params = self.routes_manager.match_route(path)
            response = resource(environ, **path_params)
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
        elif 300 <= response.status < 400:
            self.logger.warning(str(response.body))
        elif 400 <= response.status < 500:
            self.logger.error(str(response.body))
        elif response.status >= 500:
            self.logger.critical(str(response.body))

        if start_response is not None:
            start_response(response.get_status(), list(response.headers.items()))
        return response.get_body_bytes()
