import json

from typing import Generic, TypeVar
from urllib.parse import parse_qs


DEFAULT_HEADERS = [
    'ACCEPT',
    'USER-AGENT',
    'REQUEST-START-TIME',
    'ACCEPT-ENCODING',
    'HOST',
    'CONNECTION'
]

T = TypeVar("T")


class Request(Generic[T]):
    headers: dict
    _headers: dict
    params: dict
    body: T

    def __init__(self, environ: dict, body_type: type=None):
        self.headers, self._headers = self.parse_headers(environ)
        self.params = self.parse_params(environ)

        if body_type is not None:
            self.body = body_type(**self._parse_body(environ))
        else:
            self.body = self._parse_body(environ)

    @staticmethod
    def parse_headers(environ):
        """Converts the request headers into a dictionary."""
        custom_headers = {}
        default_headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-')
                if header_name in DEFAULT_HEADERS:
                    default_headers[header_name.title()] = value
                else:
                    custom_headers[header_name.title()] = value
        return custom_headers, default_headers

    @staticmethod
    def parse_params(environ):
        """Convert a query string to a dictionary."""
        query_string = environ.get('QUERY_STRING', '')
        return {key: value[0] if len(value) == 1 else value
                for key, value in parse_qs(query_string).items()}

    @staticmethod
    def _parse_body(environ) -> T:
        """Reads and decodes the body of the POST request."""
        length = int(environ.get('CONTENT_LENGTH', 0))
        if length > 0:
            body_bytes = environ['wsgi.input'].read(length)
            try:
                return json.loads(body_bytes.decode('utf-8'))
            except json.JSONDecodeError:
                return body_bytes.decode('utf-8')
        return None


__all__ = ['Request']
