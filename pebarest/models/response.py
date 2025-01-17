from typing import Optional, Union, List

from pebarest.utils import dumps


class Response:
    status: int
    headers: dict
    body: Optional[Union[dict, str]] = None

    def __init__(self, status: int, headers: dict, body: Union[dict, str]=None):
        self.status = status
        self.headers = headers
        self.body = body

    def get_body_bytes(self) -> List[bytes]:
        return [dumps(self.body)]

    def get_status(self):
        return f"{self.status} "


__all__ = ['Response']
