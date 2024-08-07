"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
07.08.24, 08:44
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Configuration objects for fields. These work similar
to the standard library annotation types, just specialized for
bindantic.
"""

import typing

from ._deps import pydantic_core

BindanticUndefinedType = pydantic_core.PydanticUndefinedType
BindanticUndefined = pydantic_core.PydanticUndefined


if typing.TYPE_CHECKING:
    from ._fields import BaseField

class FieldConfigItem[VT]:
    def __init__(self, value: VT) -> None:
        super().__init__()
        self.value = value
    pass


class Len(FieldConfigItem[int]):
    """
    Length for Array, String, Bytes, Padding
    """


class Encoding(FieldConfigItem[str]):
    """
    String encoding
    """


@typing.final
class FillDefault:
    pass

class Filler(FieldConfigItem[typing.Any | type[FillDefault]]):
    """
    Filler value for shorter arrays and strings. FillDefault
    will use the the default constructor with no parameters for filling
    """
    def __init__(self, value: typing.Any | type[FillDefault] = FillDefault) -> None:
        super().__init__(value)


class FieldConfigOptions:
    def __init__(self) -> None:
        self.items: dict[type[FieldConfigItem], FieldConfigItem] = {}
    
    def set_from_item(self, config_item: FieldConfigItem) -> None:
        self.items[type(config_item)] = config_item
    
    def get_with_error[VT](self, field: "BaseField", opt: type[FieldConfigItem[VT]], default: VT | None = None) -> VT:
        """
        Gets the value of a specific config options if it was passed, a default if not
        and throws an error if no default available.
        """
        if opt in self.items:
            return self.items[opt].value
        elif default is not None:
            return default
        else:
            raise TypeError(f"'{field.__class__.__name__}' '{field.field_name}' is missing required config option: '{opt.__name__}'")



