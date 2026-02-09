from typing import Dict, Optional, Any


class BaseAuthenticator:
    """
        Base class for authenticators. All authenticators should inherit from this class and implement the authenticate method.
    """
    def authenticate(self, request) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


__all__ = ['BaseAuthenticator']
