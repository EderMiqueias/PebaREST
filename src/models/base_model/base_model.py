import json
from datetime import datetime
from typing import Union, get_args, get_origin

from src.models.exceptions import AttrTypeError, AttrListTypeError, AttrMissingError

NoneType = type(None)


class BaseModel(dict):
    """
    O proposito da classe é ser utilizada como base para criação de objetos a partir de um dict,
    que podem ser usados como dict, e com validação de tipagem.
    """
    __attrs: tuple = ()

    def __init__(self, *args):
        self.__attrs = self.__get_attrs(self)
        for index, attr_name in enumerate(self.__attrs):
            try:
                attr_class_type = self.__check_attr_type(attr_name, args[index])
                setattr(self, attr_name, BaseModel.transform_attr(args[index], attr_class_type))
            except AttributeError:
                raise AttrMissingError(attr_name)
            except IndexError:
                if self.__check_attr_is_optional(self, attr_name):
                    if not hasattr(self, attr_name):
                        setattr(self, attr_name, None)
                    return
                raise AttrMissingError(attr_name)

        super().__init__(self.to_json())

    def __init_subclass__(cls, **kwargs):
        for hierarchical_class in cls.__mro__:
            if issubclass(hierarchical_class, BaseModel):
                cls.__annotations__.update(hierarchical_class.__annotations__)
        cls.__annotations__.pop('_BaseModel__attrs')

    def __iter__(self):
        yield from self.to_json().items()

    def __str__(self):
        return json.dumps(self.to_json())

    def __repr__(self):
        return self.__str__()

    def __setattr__(self, key, value):
        transformed_value = BaseModel.transform_attr(value, self.__annotations__[key])
        super().__setattr__(key, transformed_value)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, item):
        return getattr(self, item)

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
    def __get_attrs(cls):
        return tuple(cls.__annotations__.keys())

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

    @staticmethod
    def __transform_attr(attr, attr_class_type):
        if attr_class_type == datetime:
            return str(attr)
        if issubclass(attr_class_type, BaseModel) and isinstance(attr, dict):
            return attr_class_type.from_json(attr)
        return attr_class_type(attr)

    @staticmethod
    def __transform_list_attr(attr, attr_class_type):
        type_list = get_args(attr_class_type)
        if type_list:
            type_list = type_list[0]
            if issubclass(type_list, BaseModel):
                return list(map(lambda item: type_list.from_json(item), attr))
            return attr

    @staticmethod
    def transform_attr(attr, attr_class_type):
        class_type_origin = get_origin(attr_class_type)
        if class_type_origin in (list, tuple):
            return BaseModel.__transform_list_attr(attr, attr_class_type)
        elif class_type_origin is Union:
            return attr
        return BaseModel.__transform_attr(attr, attr_class_type)

    def __check_attr_type(self, attr_name: str, attr_value):
        attr_type = type(attr_value)
        attr_class_type = self.__annotations__[attr_name]
        if attr_type != attr_class_type:
            class_type_origin = get_origin(attr_class_type)
            class_type_args = get_args(attr_class_type)
            if class_type_origin is Union:
                if get_origin(class_type_args[0]) in (list, tuple): # é uma lista opcional
                    return attr_class_type
                if self.__type_is_subclass_of_class_tuple(attr_type, class_type_args):
                    return attr_class_type
                if not isinstance(attr_value, class_type_args):
                    raise AttrListTypeError(attr_name, class_type_args)
            elif class_type_origin in (list, tuple):
                return attr_class_type
            else:
                raise AttrTypeError(attr_name, attr_class_type)
        return attr_class_type

    def to_json(self) -> dict:
        json_object = {}
        for attr_name in self.__attrs:
            attr = getattr(self, attr_name)
            if type(attr) is datetime:
                json_object[attr_name] = str(attr)
            else:
                json_object[attr_name] = attr
        return json_object


class A(BaseModel):
    a: str
    b: datetime


a = A('a', datetime.now())
A.from_json(a)
print(a)