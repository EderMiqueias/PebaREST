import re

from typing import Optional


_PARAM_RE = re.compile(r'\{(\w+)\}')


def compile_path(path: str) -> Optional[re.Pattern]:
    """Convert a path template like /users/{id} into a compiled regex.

    Returns None for static paths that contain no parameters.
    """
    if not _PARAM_RE.search(path):
        return None
    regex = _PARAM_RE.sub(r'(?P<\1>[^/]+)', path)
    return re.compile(f'^{regex}$')


__all__ = ['compile_path']
