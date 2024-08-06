"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
06.08.24, 16:54
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Field config classes for various binary fields
"""

import typing
from typing import Callable, Any, Annotated
import dataclasses
from ._deps import pydantic


PyStructBaseTypes = bytes | int | bool | float


@dataclasses.dataclass(
    init=False, repr=True, eq=False, order=False,
    unsafe_hash=False, frozen=False, match_args=True,
    kw_only=False, slots=False, weakref_slot=False
)
class BaseField:
    """
    Class for holding configuration and info of a binary field.
    Some info is only populated during class creating
    and other information can be passed directly by the user as field config.
    """
    
    # bit width for types where that makes sense. This defines how many bits are consumed,
    # somewhat like a C bit field
    #width: Optional[int] = None
    
    # the actual python datatype to represent this field
    type_annotation: type = ...

    # The code representing this field in a python struct string
    struct_code: str = ""

    # whether this field is an outlet for a computed field, in which case
    # it will not be unpacked
    is_outlet = False

    # how many struct elements this field consumes or provides
    element_consumption: int = 1

    # how many bytes this field takes up in the structure
    bytes_consumption: int = 0

    def configure_struct_field(self, annotation: type) -> None:
        """
        To be overridden by subclasses to perform specialized initialization
        depending on the annotations.
        """
        self.type_annotation = annotation
        ...

    def unpacking_postprocessor(self, *data: PyStructBaseTypes) -> Any:          # Callable[[PyStructBaseTypes], Any] = lambda data: data
        """
        Function called after unpacking to convert the unpacked but still
        raw structure fields (bytes | int | bool | float) to a different
        higher level python object.

        To be overridden by subclasses to implement specialized behavior.
        """
        return data
    
    def packing_preprocessor(self, field: Any) -> PyStructBaseTypes:         # Callable[[Any], PyStructBaseTypes] = lambda field: field
        """
        Function called before packing to convert a higher level python object
        into rawer types (bytes | int | bool | float) that can be packed into
        a structure.

        To be overridden by subclasses to implement specialized behavior.
        """
        return field


class Uint8Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 1
        self.struct_code = "B"

Uint8 = Annotated[int, Uint8Field()]


class Uint16Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 2
        self.struct_code = "H"

Uint16 = Annotated[int, Uint16Field()]


class Uint32Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 4
        self.struct_code = "I"

Uint32 = Annotated[int, Uint32Field()]


class Uint64Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 8
        self.struct_code = "Q"

Uint64 = Annotated[int, Uint64Field()]


class Int8Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 1
        self.struct_code = "b"

Int8 = Annotated[int, Int8Field()]


class Int16Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 2
        self.struct_code = "h"

Int16 = Annotated[int, Int16Field()]


class Int32Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 4
        self.struct_code = "i"

Int32 = Annotated[int, Int32Field()]


class Int64Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 8
        self.struct_code = "q"

Int64 = Annotated[int, Int64Field()]


class Float32Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 4
        self.struct_code = "f"

Float32 = Annotated[int, Float32Field()]


class Float64Field(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 8
        self.struct_code = "d"

Float64 = Annotated[int, Float64Field()]


class CharField(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 1
        self.struct_code = "c"

Char = Annotated[int, CharField()]


class BoolField(BaseField):
    def __init__(self) -> None:
        self.bytes_consumption = 1
        self.struct_code = "?"

Bool = Annotated[int, BoolField()]


class StringField(BaseField):
    """
    fixed length string (bytes converted to string)
    """
    def __init__(self, length: int, encoding: str = "utf-8") -> None:
        self.encoding = encoding
        self.length = length

        self.bytes_consumption = length
        self.struct_code = f"{int(self.length)}s"
    
    def unpacking_postprocessor(self, data: bytes) -> str:
        data.decode(self.encoding)  # decode bytes to string

    def packing_preprocessor(self, field: str) -> bytes:
        field.encode(self.encoding) # encode string to bytes

String = Annotated[int, StringField()]


class BytesField(BaseField):
    """
    fixed length byte array (not converted to string)
    """
    def __init__(self, length: int) -> None:
        self.length = length

        self.bytes_consumption = length
        self.struct_code = f"{int(self.length)}s"

Bytes = Annotated[int, BytesField()]


class PaddingField(BaseField):
    """
    fixed length padding block
    """
    def __init__(self, length: int) -> None:
        self.length = length

        self.bytes_consumption = length
        self.struct_code = f"{int(self.length)}x"

Padding = Annotated[int, PaddingField()]


class EnumField(BaseField):
    """
    fixed length string (bytes converted to string)
    """
    def __init__(self, length: int, encoding: str = "utf-8") -> None:
        self.encoding = encoding
        self.length = length

        self.bytes_consumption = length
        self.struct_code = f"{int(self.length)}s"

    def unpacking_postprocessor(self, data: bytes) -> str:
        data.decode(self.encoding)  # decode bytes to string

    def packing_preprocessor(self, field: str) -> bytes:
        field.encode(self.encoding) # encode string to bytes


ET = typing.TypeVar("ET")
FT = typing.TypeVar("FT")
String = Annotated[int, StringField()]

# TODO: enum field continue with type parameters