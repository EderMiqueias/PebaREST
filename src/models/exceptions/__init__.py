from typing import List, Union, Tuple


class AttrTypeError(Exception):
    attr_name: str
    class_type: type

    def __init__(self, attr_name: str, class_type: type):
        self.attr_name = attr_name
        self.class_type = class_type


class AttrListTypeError(Exception):
    attr_name: str
    class_type: Union[List[type], Tuple[type]]

    def __init__(self, attr_name: str, list_type: List[type]):
        self.attr_name = attr_name
        self.list_type = list_type


class AttrMissingError(Exception):
    attr_name: str

    def __init__(self, attr_name: str):
        self.attr_name = attr_name
