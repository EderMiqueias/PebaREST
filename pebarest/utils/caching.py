import typing as t
from typing import Optional


class Missing:
    def __repr__(self) -> str:
        return "no value"

    def __reduce__(self) -> str:
        return "_missing"


_missing = Missing()
_T = t.TypeVar("_T")


class CachedProperty(property, t.Generic[_T]):
    """A :func:`property` that is only evaluated once. Subsequent access
    returns the cached value. Setting the property sets the cached
    value. Deleting the property clears the cached value, accessing it
    again will evaluate it again.

    code-block:: python

        class Example:
            @cached_property
            def value(self):
                # calculate something important here
                return 42

        e = Example()
        e.value  # evaluates
        e.value  # uses cache
        e.value = 16  # sets cache
        del e.value  # clears cache

    If the class defines ``__slots__``, it must add ``_cache_{name}`` as
    a slot. Alternatively, it can add ``__dict__``, but that's usually
    not desirable.
    """
    def __init__(
        self,
        fget: t.Callable[[t.Any], _T],
        name: Optional[str] = None,
        doc: Optional[str] = None,
    ) -> None:
        super().__init__(fget, doc=doc)
        self.__name__ = name or fget.__name__
        self.slot_name = f"_cache_{self.__name__}"
        self.__module__ = fget.__module__

    def __set__(self, obj: object, value: _T) -> None:
        if hasattr(obj, "__dict__"):
            obj.__dict__[self.__name__] = value
        else:
            setattr(obj, self.slot_name, value)

    def __get__(self, obj: object, type: type = None) -> _T:  # type: ignore
        if obj is None:
            return self  # type: ignore

        obj_dict = getattr(obj, "__dict__", None)

        if obj_dict is not None:
            value: _T = obj_dict.get(self.__name__, _missing)
        else:
            value = getattr(obj, self.slot_name, _missing)  # type: ignore[arg-type]

        if value is _missing:
            value = self.fget(obj)  # type: ignore

            if obj_dict is not None:
                obj.__dict__[self.__name__] = value
            else:
                setattr(obj, self.slot_name, value)

        return value

    def __delete__(self, obj: object) -> None:
        if hasattr(obj, "__dict__"):
            del obj.__dict__[self.__name__]
        else:
            setattr(obj, self.slot_name, _missing)
