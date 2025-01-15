from typing import Optional, Union


class Response:
    status: int
    headers: dict
    body: Optional[dict, str]

    def __init__(self, status: int, headers: dict, body: Union[dict, str]=None):
        self.status = status
        self.headers = headers
        self.body = body


__all__ = ['Response']
