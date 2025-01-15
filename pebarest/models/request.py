from typing import Optional


class Request:
    headers: dict
    params: dict
    body: Optional[dict]

    def __init__(self, environ):
        self.headers = environ['HEADERS']
        self.params = environ['PARAMS']
        self.body = environ['BODY']

__all__ = ['Request']
