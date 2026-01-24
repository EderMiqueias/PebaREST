from datetime import datetime, date
from typing import Any


class JsonClass:
    def __iter__(self):
        raise NotImplementedError()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{" + ", ".join(f"{to_double_quoted_string(key)}: {to_serializable(val)}" for key, val in self) + "}"


def to_double_quoted_string(value) -> str:
    """
    Converts a string value to a double-quoted representation.

    :param value: String value to be converted.
    :return: String with double quotes.
    """
    return '"{}"'.format(value.replace("\\", "\\\\").replace("\"", "\\\""))


def to_serializable(value: Any) -> str:
    """
    Converts a value to a serializable string.

    :param value: Value to be converted.
    :return: Serializable string.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, str):
        return to_double_quoted_string(value)
    elif isinstance(value, (int, float)):
        return repr(value)
    elif isinstance(value, dict):
        return "{" + ", ".join(f"{to_double_quoted_string(key)}: {to_serializable(val)}" for key, val in value.items()) + "}"
    elif isinstance(value, (list, tuple, set)):
        return "[" + ", ".join(to_serializable(item) for item in value) + "]"
    elif value is None:
        return "null"
    elif isinstance(value, (datetime, date)):
        return to_double_quoted_string(value.isoformat())
    elif isinstance(value, JsonClass):
        return value.__repr__()
    else:
        raise TypeError(f"Type {type(value)} is not supported.")


def dumps(data: Any) -> bytes:
    """
    Serializes various data types to bytes (UTF-8), in a format similar to JSON.
    """
    return to_serializable(data).encode("utf-8")


def get_json_str_type_from_type(obj_type: type) -> str:
    if obj_type == str:
        return 'string'
    if obj_type == int:
        return 'integer'
    if obj_type == float:
        return 'number'
    if obj_type == bool:
        return 'boolean'
    if obj_type == list:
        return 'array'
    return 'object'
