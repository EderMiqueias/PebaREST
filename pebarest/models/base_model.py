from datetime import datetime
from typing import Any, Union, List, Dict, Set, get_origin, get_args, Optional
import collections.abc

from pebarest.exceptions import AttrTypeError, AttrListTypeError, AttrMissingError
from pebarest.utils.json import JsonClass

NoneType = type(None)


class BaseModel(JsonClass):
    """
    The purpose of the class is to be used as a base for creating objects from a dict,
    which can be used as a dict, and with typing validation.
    """
    __attrs: tuple = ()

    def __init__(self, **kwargs):
        self.__attrs = self.__get_attrs()
        for attr_name in self.__attrs:
            try:
                setattr(self, attr_name, self.check_attr_type(attr_name, kwargs[attr_name]))
            except KeyError:
                raise AttrMissingError(attr_name)
            except AttributeError:
                raise AttrMissingError(attr_name)
            except TypeError:
                raise AttrTypeError(attr_name, self.__annotations__[attr_name])
            except IndexError:
                if self.__check_attr_is_optional(self, attr_name):
                    if not hasattr(self, attr_name):
                        setattr(self, attr_name, None)
                    return
                raise AttrMissingError(attr_name)

    def __init_subclass__(cls, **kwargs):
        for hierarchical_class in cls.__mro__:
            if issubclass(hierarchical_class, BaseModel):
                cls.__annotations__.update(hierarchical_class.__annotations__)

    def __iter__(self):
        # TODO: ISSO PODERIA SER FEITO DE FORMA MAIS OTIMIZADA
        yield from self.to_dict().items()

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def __dict__(self):
        return self.to_dict()

    @staticmethod
    def __check_attr_is_optional(cls, attr_name) -> bool:
        attr_class_type = cls.__annotations__[attr_name]
        if get_origin(attr_class_type) is Union:
            if NoneType in get_args(attr_class_type):
                return True
        return False

    def __get_attrs(self) -> list:
        attrs = list(self.__annotations__.keys())
        attrs.remove('_BaseModel__attrs')
        return attrs

    def check_attr_type(self, attr_name: str, value):
        type_hint = self.__annotations__[attr_name]
        if isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
            if isinstance(value, dict):
                return type_hint(**value)
            if isinstance(value, type_hint):
                return value

        if not self.is_instance_of(value, type_hint):
            raise AttrTypeError(attr_name, type_hint)

        return value

    def is_instance_of(self, value, type_hint) -> bool:
        """
            Checks whether the value belongs to the given type, including support for typing generics.
        """
         # TODO: entender o __new__ e como reutilizar uma instancia de classe para reduzir o tempo de processamento e mover as validações para um dict
        if type_hint is Any:
            return True

        if isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
            return isinstance(value, (type_hint, dict))

        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is None:
            if isinstance(type_hint, type):
                return isinstance(value, type_hint)
            return True

        if origin is Union:
            return any(self.is_instance_of(value, arg) for arg in args)

        if origin in (list, List, collections.abc.Sequence, collections.abc.Iterable):
            if not isinstance(value, (list, tuple)):
                return False
            return not args or all(self.is_instance_of(item, args[0]) for item in value)

        if origin in (dict, Dict, collections.abc.Mapping):
            if not isinstance(value, dict):
                return False
            return not args or all(
                self.is_instance_of(k, args[0]) and self.is_instance_of(v, args[1])
                for k, v in value.items()
            )

        if origin in (set, Set, collections.abc.Set):
            if not isinstance(value, set):
                return False
            return not args or all(self.is_instance_of(item, args[0]) for item in value)

        return isinstance(value, origin)

    @classmethod
    def get_openapi_schema(cls) -> Dict[str, Any]:
        """
        Generates the OpenAPI 3.1.0 schema for the class based on its type annotations.
        Implements automatic conversion of Python types to JSON Schema.
        """
        properties = {}
        required = []

        for attr_name, type_hint in cls.__annotations__.items():
            if attr_name.startswith(f'_{cls.__name__}__') or attr_name == '_BaseModel__attrs':
                continue

            properties[attr_name] = cls._type_to_schema(type_hint)

            if not cls.__check_attr_is_optional(cls, attr_name):
                required.append(attr_name)

        schema = {
            "type": "object",
            "properties": properties
        }

        if required:
            schema["required"] = required

        return schema

    @classmethod
    def _type_to_schema(cls, type_hint: Any) -> Dict[str, Any]:
        """
        Maps Python types and generics from the typing library to JSON Schema (OAS 3.1.0).
        """
        if isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
            return type_hint.get_openapi_schema()

        origin = get_origin(type_hint)
        args = get_args(type_hint)

        mapping = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            datetime: {"type": "string", "format": "date-time"},
            Any: {},
            NoneType: {"type": "null"}
        }

        if origin is None:
            return mapping.get(type_hint, {"type": "string"})

        if origin is Union:
            sub_schemas = [cls._type_to_schema(arg) for arg in args]
            return {"anyOf": sub_schemas}

        if origin in (list, List, collections.abc.Sequence):
            item_type = args[0] if args else Any
            return {
                "type": "array",
                "items": cls._type_to_schema(item_type)
            }

        if origin in (dict, Dict, collections.abc.Mapping):
            value_type = args[1] if len(args) > 1 else Any
            return {
                "type": "object",
                "additionalProperties": cls._type_to_schema(value_type)
            }

        return {"type": "object"}

    def to_dict(self) -> dict:
        json_object = {}
        for attr_name in self.__attrs:
            attr = getattr(self, attr_name)
            if type(attr) is datetime:
                json_object[attr_name] = str(attr)
            else:
                json_object[attr_name] = attr
        return json_object


__all__ = ['BaseModel', 'NoneType']
