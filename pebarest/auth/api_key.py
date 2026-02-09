from typing import Dict, Optional, Any

from pebarest.auth import BaseAuthenticator
from pebarest.exceptions.app_exeptions import UnauthorizedError


class APIKeyAuthenticator(BaseAuthenticator):
    """
    Static key authenticator.
    Allows multiple keys and client metadata mapping.
    """
    __valid_keys__ = {}

    def __init__(self,
                 valid_keys: Dict[str, Any],
                 header_name: str = "X-API-Key",
                 query_param: Optional[str] = None):
        self.__valid_keys__ = valid_keys
        self.header_name = header_name
        self.query_param = query_param

    @property
    def valid_keys(self) -> Dict[str, Any]:
        """
            Returns a dict of valid keys that the authenticator expects to find in the request for authentication.
        """
        return self.__valid_keys__

    def add_valid_key(self, key: str, client_id: Any):
        """
            Adds a valid key to the authenticator. This can be used to add keys at runtime if needed.
        """
        if not isinstance(key, str):
            raise ValueError("key must be a string.")
        self.__valid_keys__[key] = client_id

    def authenticate(self, request) -> Optional[Dict[str, Any]]:
        token = request.headers.get(self.header_name)

        if not token and self.query_param:
            token = request.query_params.get(self.query_param)

        if token in self.valid_keys:
            return {
                "client_id": self.valid_keys[token],
                "auth_method": "API-Key"
            }

        raise UnauthorizedError()


__all__ = ['APIKeyAuthenticator']
