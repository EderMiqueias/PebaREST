from datetime import datetime
from typing import Union, List, Dict, get_origin, get_args

from pebarest.exceptions import AttrTypeError, AttrListTypeError, AttrMissingError, EntityAttrTypeError
from pebarest.utils.json import JsonClass

NoneType = type(None)


class BaseModel(JsonClass):
    """
    O proposito da classe é ser utilizada como base para criação de objetos a partir de um dict,
    que podem ser usados como dict, e com validação de tipagem.
    """
    __attrs: tuple = ()

    def __init__(self, **kwargs):
        self.__attrs = self.__get_attrs(self)
        for attr_name in self.__attrs:
            try:
                if instancied_subclass := self.check_attr_type(attr_name, kwargs[attr_name]):
                    setattr(self, attr_name, instancied_subclass)
                else:
                    setattr(self, attr_name, kwargs[attr_name])
            except KeyError:
                raise AttrMissingError(attr_name)
            except AttributeError:
                raise AttrMissingError(attr_name)
            except TypeError:
                raise EntityAttrTypeError(attr_name)
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

    def check_attr_type(self, attr_name: str, value):
        type_hint = self.__annotations__[attr_name]
        if issubclass(type_hint, BaseModel):
            if isinstance(value, type_hint):
                return value
            return type_hint(**value)

        if not self.is_instance_of(value, type_hint):
            raise AttrTypeError(attr_name, self.__annotations__[attr_name])

    def is_instance_of(self, value, type_hint) -> bool:
        """
            Checks whether the value belongs to the given type, including support for typing generics.
        """
        origin = get_origin(type_hint)

        if origin is None:
            return isinstance(value, type_hint)

        args = get_args(type_hint)

        if origin is Union:
            return any(self.is_instance_of(value, arg) for arg in args)

        if origin in (list, List):
            return isinstance(value, list) and all(map(lambda item: self.is_instance_of(item, args[0]), value))

        if origin in (dict, Dict):
            return (isinstance(value, dict) and
                    all(map(lambda kv: self.is_instance_of(kv[0], args[0]) and
                                       self.is_instance_of(kv[1], args[1]), value.items())))
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
