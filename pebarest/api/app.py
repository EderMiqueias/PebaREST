import logging

from typing import Union, Dict, Type, Any

from pebarest import BaseModel
from pebarest.models import Resource, Response, DefaultErrorResponse
from pebarest.exceptions import RouteAlreadyExistsError, MethodNotAllowedError, NotFoundError, AttrMissingError, \
    AttrTypeError
from pebarest.models.response import ErrorResponse
from pebarest.testing import UnitTestGenerator
from pebarest.testing.base_test_generator import TestGenerator
from pebarest.testing.test_client import TestClient
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
    def routes(self) -> Dict[str, Resource]:
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
    error_format: Type[ErrorResponse]
    import_name: str
    default_headers: dict
    is_debug: bool
    testing_generator: TestGenerator
    
    def __init__(
            self,
            import_name: str,
            default_headers: dict=None,
            is_debug: bool=True,
            generate_docs: bool=False,
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

        self.routes_manager: RoutesManager = routes_manager()
        self.headers = default_headers

        if not issubclass(error_format, dict):
            raise TypeError('The error format class must be a subclass of dict.')
        self.error_format=error_format
        self.testing_generator = testing_generator(self)
        self.__tests_generated = False

    def add_route(self, path: str, resource: Union[object, Resource]):
        if isinstance(resource, Resource):
            if not resource.headers:
                resource.headers = self.headers
            self.routes_manager.add_route(path, resource)
        else:
            resource = Resource.from_anonymous_object(resource, self.headers)
            self.routes_manager.add_route(path, resource)
    
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
            resource = self.routes_manager.get_route_resource(environ['PATH_INFO'])
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
        elif 300 <= response.status < 400:
            self.logger.warning(str(response.body))
        elif 400 <= response.status < 500:
            self.logger.error(str(response.body))
        elif response.status >= 500:
            self.logger.critical(str(response.body))

        if start_response is not None:
            start_response(response.get_status(), list(response.headers.items()))
        return response.get_body_bytes()
