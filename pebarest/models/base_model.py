import json
from datetime import datetime
from typing import Union, List, Dict, get_origin, get_args

from pebarest.exceptions import AttrTypeError, AttrListTypeError, AttrMissingError


NoneType = type(None)


class BaseModel:
    """
    O proposito da classe é ser utilizada como base para criação de objetos a partir de um dict,
    que podem ser usados como dict, e com validação de tipagem.
    """
    __attrs: tuple = ()

    def __init__(self, *args):
        self.__attrs = self.__get_attrs(self)
        for index, attr_name in enumerate(self.__attrs):
            try:
                self.check_attr_type(attr_name, args[index])
                setattr(self, attr_name, args[index])
            except AttributeError:
                raise AttrMissingError(attr_name)
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
        yield from self.to_dict().items()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return json.dumps(self.to_dict())

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def __dict__(self):
        return self.to_dict()

    @staticmethod
    def _get_internal_attrs_keys() -> tuple:
        return '_BaseModel__attrs', '_BaseModel__sub_instances'

    @staticmethod
    def __type_is_subclass_of_class_tuple(class_type, union_class_type):
        for ct_item in get_args(union_class_type):
            if issubclass(ct_item, class_type):
                return True
        return False

    @staticmethod
    def __check_item(item) -> bool:
        try:
            if get_origin(item[1]) is Union:
                return BaseModel.__type_is_subclass_of_class_tuple(BaseModel, item[1])
            return issubclass(item[1], BaseModel)
        except AttrTypeError:
            return False

    @staticmethod
    def __get_attrs_instance(cls) -> dict:
        return dict(
            filter(BaseModel.__check_item, cls.__annotations__.items())
        )

    @staticmethod
    def __check_attr_is_optional(cls, attr_name) -> bool:
        attr_class_type = cls.__annotations__[attr_name]
        if get_origin(attr_class_type) is Union:
            if NoneType in get_args(attr_class_type):
                return True
        return False

    @staticmethod
    def __get_attrs(cls) -> tuple:
        attrs = list(cls.__annotations__.keys())
        attrs.remove('_BaseModel__attrs')
        return tuple(attrs)

    @staticmethod
    def __get_instance_from_correct_class(cls, union_class_type: Union, payload: dict, attr_name: str):
        class_type_args = get_args(union_class_type)
        for ct_arg in class_type_args:
            try:
                return ct_arg.from_json(payload[attr_name])
            except AttrTypeError:
                return payload[attr_name]
            except (AttrMissingError, AttributeError):
                pass
        if hasattr(cls, attr_name):
            return getattr(cls, attr_name)

    @staticmethod
    def __from_key(cls, payload: dict, key: str):
        attrs_sub_instances = cls.__get_attrs_instance(cls)
        if key in attrs_sub_instances:
            if get_origin(attrs_sub_instances[key]) is Union:
                # if NoneType in get_args(attrs_sub_instances[key]) and (key not in payload.keys()) and hasattr(cls, key):
                #     return getattr(cls, key)
                return cls.__get_instance_from_correct_class(cls, attrs_sub_instances[key], payload, key)
            return attrs_sub_instances[key].from_json(payload[key])
        elif cls.__check_attr_is_optional(cls, key) and (key not in payload.keys()) and hasattr(cls, key):
            return getattr(cls, key)
        return payload.get(key)

    @classmethod
    def from_json(cls, payload: dict):
        type_payload = type(payload)
        if type_payload is dict:
            attrs = cls.__get_attrs(cls)
            return cls(
                *(cls.__from_key(cls, payload, attr_key) for attr_key in attrs)
            )
        if issubclass(type_payload, BaseModel):
            return payload
        raise AttrTypeError(cls.__name__, dict)

    def check_attr_type(self, attr_name: str, value):
        if not self.is_instance_of(value, self.__annotations__[attr_name]):
            raise AttrTypeError(attr_name, self.__annotations__[attr_name])

    def is_instance_of(self, value, type_hint) -> bool:
        """
            Checks whether the value belongs to the given type, including support for typing generics.
        """
        origin = get_origin(type_hint)

        if origin is None:
            return isinstance(value, type_hint)

        if origin is Union:
            return any(self.is_instance_of(value, arg) for arg in get_args(type_hint))

        if origin is list or origin is List:
            if not isinstance(value, list):
                return False
            element_type = get_args(type_hint)[0]
            return all(self.is_instance_of(item, element_type) for item in value)

        if origin is dict or origin is Dict:
            if not isinstance(value, dict):
                return False
            key_type, value_type = get_args(type_hint)
            return all(self.is_instance_of(k, key_type) and self.is_instance_of(v, value_type) for k, v in value.items())

        return isinstance(value, origin)


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
