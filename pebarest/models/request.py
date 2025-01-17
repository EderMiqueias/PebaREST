from typing import Optional
from urllib.parse import parse_qs


class Request:
    headers: dict
    params: dict
    body: Optional[dict]

    def __init__(self, environ):
        self.headers = self.parse_headers(environ)
        self.params = self.parse_params(environ)
        self.body = {}

    @staticmethod
    def parse_headers(environ):
        """Converts the request headers into a dictionary."""
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        return headers

    @staticmethod
    def parse_params(environ):
        """Convert a query string to a dictionary."""
        query_string = environ.get('QUERY_STRING', '')
        return {key: value[0] if len(value) == 1 else value
                for key, value in parse_qs(query_string).items()}

__all__ = ['Request']
