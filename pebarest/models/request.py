from typing import Optional


class Request:
    headers: dict
    params: dict
    body: Optional[dict]

    def __init__(self, headers: dict, params: dict, body: dict=None):
        self.headers = headers
        self.params = params
        self.body = body

__all__ = ['Request']
