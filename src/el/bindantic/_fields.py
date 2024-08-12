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
import dataclasses
import abc
import enum
from collections import deque
from typing import Any, Annotated, override
from copy import deepcopy
from ._deps import pydantic, annotated_types
from ._config import *


PyStructBaseTypes = bytes | int | bool | float


@dataclasses.dataclass(
    init=False, repr=True, eq=False, order=False,
    unsafe_hash=False, frozen=False, match_args=True,
    kw_only=False, slots=False, weakref_slot=False
)
class BaseField(abc.ABC):
    """
    Class for holding configuration and info of a binary field.
    Some info is only populated during class creating
    and other information can be passed directly by the user as field config.
    """
    
    def __init__(self) -> None:
        super().__init__()

        # set of python types that are supported for conversion
        self.supported_py_types: tuple[type, ...] = ...

        # the name of the field in the structure (or outlet source if field is an outlet)
        self.field_name: str = ...
        # the field info instance of the corresponding pydantic field
        self.pydantic_field: pydantic.fields.FieldInfo = ...
        # the actual python datatype to represent this field
        self.type_annotation: type = ...
        # any annotation metadata passed via typing.Annotated
        self.annotation_metadata: list[Any] = ...
        # whether this field is a top level field in a struct or a nested field in an array
        self.is_top_level: bool = ...

        # config options provided by user
        self.config_options = FieldConfigOptions()

        # The code representing this field in a python struct string
        self.struct_code: str = ""

        # whether this field is an outlet for a computed field, in which case
        # it will not be unpacked
        self.is_outlet: bool = False
        # the name of the actual outlet pydantic field if it is an outlet
        self.outlet_name: str = ""

        # how many struct elements this field consumes or provides (usually 1 )
        self.element_consumption: int = 1

        # how many bytes this field takes up in the structure (must be set)
        self.bytes_consumption: int = ...

    def configure_struct_field(self, field_name: str, pydantic_field: pydantic.fields.FieldInfo, is_top_level: bool) -> None:
        """
        Called during struct construction to configure the field with all
        additional information about it provided by pydantic.

        is_top_level==True indicates that the provided FieldInfo instance is
        directly associated with a top-level field in a structure and can be
        modified to change the behavior of pydantic field validation.
        Non-top-level fields' FieldInfo instance is not associated with pydantic
        and does therefor not support this behavior.
        """
        self.pydantic_field = pydantic_field
        self.type_annotation = pydantic_field.annotation
        self.annotation_metadata = pydantic_field.metadata
        self.is_top_level = is_top_level

        # if this is a top level pydantic field we check for outlets
        if field_name.endswith("_outlet") and self.is_top_level:
            self.outlet_name = field_name
            self.field_name = field_name.removesuffix("_outlet")
            self.is_outlet = True
        else:
            self.field_name = field_name
        
        # read any field config items from metadata
        self.config_options.set_from_metadata(self.annotation_metadata)

        self._type_check()
        self._configure_specialization()
 
    def _type_check(self) -> None:
        """
        Returns true if the type annotation matches the expected type for the 
        field type. This can be overridden by subclasses for special behavior
        """
        if not issubclass(self.type_annotation, self.supported_py_types):
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must resolve to one of {self.supported_py_types}, not '{self.type_annotation}'")
        
    def _configure_specialization(self) -> None:
        """
        Can be overridden by subclasses to perform specialized initialization
        depending on the annotations.
        """
        ...

    def unpacking_postprocessor(self, data: tuple[PyStructBaseTypes, ...]) -> Any:          # Callable[[PyStructBaseTypes], Any] = lambda data: data
        """
        Function called after unpacking to convert the unpacked but still
        raw structure fields (bytes | int | bool | float) to a different
        higher level python object.

        Can be overridden by subclasses to implement specialized behavior.
        """
        return data[0]
    
    def packing_preprocessor(self, field: Any) -> tuple[PyStructBaseTypes, ...]:         # Callable[[Any], PyStructBaseTypes] = lambda field: field
        """
        Function called before packing to convert a higher level python object
        into rawer types (bytes | int | bool | float) that can be packed into
        a structure.

        Can be overridden by subclasses to implement specialized behavior.
        """
        field = self.type_annotation(field) # ensure correct type
        return (field, )

    def is_equivalent(self, other: "BaseField") -> bool:
        """
        Checks if the TYPE of the field is equivalent. This can be overridden
        by subclasses to implement special checks such as bit width for integers.
        
        Note: This cannot be __eq__ because for some reason that throws off pydantic
        and gives errors in schema generation when used in deque (weird error?)
        """
        if not isinstance(other, self.__class__):
            return False
        return True


def get_field_from_field_info(
    field_name: str,
    pydantic_field: pydantic.fields.FieldInfo,
    is_top_level: bool
) -> BaseField | None:
    """
    Processes the provided type information and metadata from pydantic
    to extract and configure the appropriate structure
    field class instance to represent this field.

    is_top_level==True indicates that the provided FieldInfo instance is
    directly associated with a top-level field in a structure and can be
    modified to change the behavior of pydantic field validation.
    Non-top-level fields' FieldInfo instance is not associated with pydantic
    and does therefor not support this behavior.
    """
    raw_field = get_raw_field_field_info(pydantic_field)
    if raw_field is None:
        return None

    # deepcopy the instance from annotations so the provided config is 
    # kept but multiple fields with the same shortcut type-alias don't
    # share a single field instance
    struct_field = deepcopy(raw_field)
    # configure the field
    struct_field.configure_struct_field(
        field_name,
        pydantic_field,
        is_top_level
    )
    return struct_field

def get_raw_field_field_info(
    pydantic_field: pydantic.fields.FieldInfo,
) -> BaseField | None:
    """
    Processes the provided type information and metadata from pydantic
    to extract the appropriate structure field class instance to represent 
    this field.
    """
    for meta_element in pydantic_field.metadata:
        match meta_element:
            case BaseField():   # struct field found
                return meta_element
    # TODO: add support for substructures
    return None # No metadata found to identify this as a struct field


OT = typing.TypeVar("OT")
Outlet = Annotated[OT, pydantic.Field(default=None, init=False, exclude=True)]


class IntegerField(BaseField):
    def __init__(self, size: int, code: str, signed: bool) -> None:
        super().__init__()
        self.supported_py_types = (int, )
        self.bytes_consumption = size
        self.struct_code = code
        self.signed = signed
    
    @staticmethod
    def range_limit(signed: bool, bits: int) -> pydantic.fields.FieldInfo:
        if signed:
            bits -= 1
            return pydantic.Field(ge=-(2**bits), lt=(2**bits))
        else:
            return pydantic.Field(ge=0, lt=(2**bits))
    
    @override
    def is_equivalent(self, other: "IntegerField") -> bool:
        if not super().is_equivalent(other):    # class type check
            return False
        return (    # bit-width and signed-ness check
            other.bytes_consumption == self.bytes_consumption
            and other.signed == self.signed
        )

Uint8 = Annotated[int, IntegerField(1, "B", False), IntegerField.range_limit(False, 8)]
Uint16 = Annotated[int, IntegerField(2, "H", False), IntegerField.range_limit(False, 16)]
Uint32 = Annotated[int, IntegerField(4, "I", False), IntegerField.range_limit(False, 32)]
Uint64 = Annotated[int, IntegerField(8, "Q", False), IntegerField.range_limit(False, 64)]
Int8 = Annotated[int, IntegerField(1, "b", True), IntegerField.range_limit(True, 8)]
Int16 = Annotated[int, IntegerField(2, "h", True), IntegerField.range_limit(True, 16)]
Int32 = Annotated[int, IntegerField(4, "i", True), IntegerField.range_limit(True, 32)]
Int64 = Annotated[int, IntegerField(8, "q", True), IntegerField.range_limit(True, 64)]


class EnumField[ET: enum.Enum](IntegerField):
    """
    Integer converted to  (bytes converted to string)
    """
    def __init__(self, size: int, code: str, signed: bool) -> None:
        super().__init__(size, code, signed)
        self.supported_py_types = (enum.Enum, enum.IntEnum, enum.Flag, enum.IntFlag) # see _type_check() for details
        self.type_annotation: type[enum.Enum]
    
    @classmethod
    def check_in_range(cls, v: enum.Enum, signed: bool, bits: int, fn: str = "") -> None:
        if signed:
            ge=-(2 ** (bits - 1))
            lt=(2 ** (bits - 1))
        else:
            ge=0
            lt=(2 ** bits)
        
        if not (v.value >= ge and v.value < lt):
            field_name_part = f" '{fn}'" if fn != "" else ""
            value_part = f"{v.__class__.__name__}.{v.name} = {v.value}" if isinstance(v, (enum.IntEnum, enum.IntFlag, )) else f"{v} = {v.value}"
            raise ValueError(f"'{cls.__name__}'{field_name_part} value {value_part} overflows the available range for {"" if signed else "U"}int{bits} ({ge} <= val <= {lt - 1})")

    @staticmethod
    def range_limit(signed: bool, bits: int) -> pydantic.AfterValidator:
        def check(v: enum.Enum) -> enum.Enum:
            EnumField.check_in_range(v, signed, bits)
            return v
        return pydantic.AfterValidator(check)

    @override
    def _type_check(self) -> None:
        if (
            not issubclass(self.type_annotation, self.supported_py_types)
            or issubclass(self.type_annotation, enum.StrEnum)
        ): # don't allow string value types
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must resolve to a subclass of {self.supported_py_types} and not '{enum.StrEnum}'. {self.type_annotation} does not meet these requirements.")
        
    @override
    def _configure_specialization(self) -> None:
        # make sure all values are in range already during structure creation
        for e in self.type_annotation:
            self.check_in_range(e, self.signed, self.bytes_consumption * 8, self.field_name)

    @override
    def unpacking_postprocessor(self, data: tuple[int, ...]) -> ET:
        return self.type_annotation(data[0])   # type_annotation should be the enum

    @override
    def packing_preprocessor(self, field: ET) -> tuple[int, ...]:
        field = self.type_annotation(field) # ensure correct type
        return (field.value, )  # get numerical enum value

ET = typing.TypeVar("ET")

EnumU8 = Annotated[ET, EnumField[ET](1, "B", False), EnumField.range_limit(False, 8)]
EnumU16 = Annotated[ET, EnumField[ET](2, "H", False), EnumField.range_limit(False, 16)]
EnumU32 = Annotated[ET, EnumField[ET](4, "I", False), EnumField.range_limit(False, 32)]
EnumU64 = Annotated[ET, EnumField[ET](8, "Q", False), EnumField.range_limit(False, 64)]
Enum8 = Annotated[ET, EnumField[ET](1, "b", True), EnumField.range_limit(True, 8)]
Enum16 = Annotated[ET, EnumField[ET](2, "h", True), EnumField.range_limit(True, 16)]
Enum32 = Annotated[ET, EnumField[ET](4, "i", True), EnumField.range_limit(True, 32)]
Enum64 = Annotated[ET, EnumField[ET](8, "q", True), EnumField.range_limit(True, 64)]


class FloatField(BaseField):
    def __init__(self, size: int, code: str) -> None:
        super().__init__()
        self.supported_py_types = (float, )
        self.bytes_consumption = size
        self.struct_code = code

Float32 = Annotated[float, FloatField(4, "f")]
Float64 = Annotated[float, FloatField(8, "d")]


class CharField(BaseField):
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (str, )
        self.bytes_consumption = 1
        self.struct_code = "c"

        self.encoding: str = ...
    
    @override
    def _configure_specialization(self) -> None:
        self.encoding = self.config_options.get_with_error(self, EncodingInfo, "utf-8")

    @override  
    def unpacking_postprocessor(self, data: tuple[bytes, ...]) -> str:
        return data[0].decode(self.encoding)  # decode bytes to string

    @override
    def packing_preprocessor(self, field: str) -> tuple[bytes, ...]:
        field = self.type_annotation(field) # ensure correct type
        return (field.encode(self.encoding), ) # encode string to bytes

Char = Annotated[str, CharField(), Len(1, min="same")]


class BoolField(BaseField):
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (bool, )
        self.bytes_consumption = 1
        self.struct_code = "?"

Bool = Annotated[bool, BoolField()]


class StringField(BaseField):
    """
    fixed length string (bytes up to the first null byte are 
    converted to string and any information past that is discarded)
    """
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (str, )

        self.length: int = ...
        self.encoding: str = ...
    
    @override
    def _configure_specialization(self) -> None:
        self.length = self.config_options.get_with_error(self, LenInfo)
        self.encoding = self.config_options.get_with_error(self, EncodingInfo, "utf-8")
        self.struct_code = f"{int(self.length)}s"
        self.bytes_consumption = self.length

    @override  
    def unpacking_postprocessor(self, data: tuple[bytes, ...]) -> str:
        string_portions = data[0].split(b"\0")
        if len(string_portions) == 0:
            return ""
        else:
            return string_portions[0].decode(self.encoding)  # decode bytes to string

    @override
    def packing_preprocessor(self, field: str) -> tuple[bytes, ...]:
        field = self.type_annotation(field) # ensure correct type
        return (field.encode(self.encoding), ) # encode string to bytes

String = Annotated[str, StringField()]


class BytesField(BaseField):
    """
    fixed length byte array (not converted to string, all
    bytes are preserved as is)
    """
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (bytes, )

        self.length: int = ...
    
    @override
    def _configure_specialization(self) -> None:
        self.length = self.config_options.get_with_error(self, LenInfo)
        self.struct_code = f"{int(self.length)}s"
        self.bytes_consumption = self.length
        
Bytes = Annotated[bytes, BytesField()]


class PaddingField(BaseField):
    """
    fixed length padding block
    """
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (None, )

        self.length: int = ...
        
    @override
    def _type_check(self) -> None:
        if self.type_annotation is not type(None):
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must resolve to type 'None', not '{self.type_annotation}'")
    
    @override
    def _configure_specialization(self) -> None:
        self.length = self.config_options.get_with_error(self, LenInfo)
        self.struct_code = f"{int(self.length)}x"
        self.bytes_consumption = self.length
        # padding bytes are not converted to any python objects
        self.element_consumption = 0

    @override
    def unpacking_postprocessor(self, data: tuple[PyStructBaseTypes, ...]) -> None:
        return None
    
    @override
    def packing_preprocessor(self, field: Any) -> tuple[PyStructBaseTypes, ...]:
        return ()

Padding = Annotated[None, PaddingField(), pydantic.Field(exclude=True, default=None, init=False)]


class ArrayField(BaseField):
    """
    fixed length array of another binary capable type
    """
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (list, tuple, set, frozenset, deque)
        
        self.element_field: BaseField = ...
        self.filler: Any | BindanticUndefinedType = ...
        self.parse_mode: FillerParseMode = ...
    
    @override
    def _type_check(self) -> None:
        if not issubclass(typing.get_origin(self.type_annotation), self.supported_py_types):
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must resolve to one of {self.supported_py_types}, not '{typing.get_origin(self.type_annotation)}'")

        # extract and check the element type
        try:
            element_type_annotation = typing.get_args(self.type_annotation)[0]
        except KeyError:
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must be subscripted with an element type")
        
        # TODO: make sure this also works for substructures
        # create a pydantic field info by passing the entire annotation. If the type is annotated, 
        # this does all the heavy of reading the annotated metadata, processing pydantic related 
        # field info (not relevant for pydantic here because this is only our instance but we may
        # also require some of the parsed information) and saving datatype and annotation metadata
        # in the same way it is done with top level pydantic fields. This way, the get_element_from_type_data
        # function can create a bindantic field from the data.
        sub_field_info = pydantic.fields.FieldInfo.from_annotation(element_type_annotation)
        self.element_field = get_field_from_field_info(
            self.field_name + ".__element__",
            sub_field_info,
            False
        )
        if self.element_field is None:
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must be subscripted with a binary-capable field type, not '{element_type_annotation}'")

        if isinstance(self.element_field, PaddingField):
            raise TypeError(f"Elements of '{self.__class__.__name__}' '{self.field_name}' should not be 'Padding'. Use Padding directly.")

    @override
    def _configure_specialization(self) -> None:
        self.length = self.config_options.get_with_error(self, LenInfo)
        self.filler, self.parse_mode = self.config_options.get_with_error(self, FillerInfo, (BindanticUndefined, "keep"))

        if self.parse_mode == "auto":
            if issubclass(typing.get_origin(self.type_annotation), (set, frozenset, )):
                self.parse_mode = "remove"
            else:
                self.parse_mode = "strip-trailing"

        self.struct_code = "".join([self.element_field.struct_code] * self.length)
        self.bytes_consumption = self.length * self.element_field.bytes_consumption
        self.element_consumption = self.length * self.element_field.element_consumption
    
    @override
    def unpacking_postprocessor(self, data: tuple[PyStructBaseTypes, ...]) -> typing.Iterable:
        # create element if filler is default constructor
        if self.filler == FillDefaultConstructor:
            filler_value = self.element_field.type_annotation()
        else:
            filler_value = self.filler

        # split up struct elements for each array element and post-process them.
        values = [el for i in range(self.length)
            if ((el := self.element_field.unpacking_postprocessor(
                    data[   # pull out the amount of data elements consumed by the inner element type
                        (i * self.element_field.element_consumption) 
                        : 
                        ((i+1) * self.element_field.element_consumption)
                    ]
                )
            ) != filler_value or self.parse_mode != "remove")    # if not in remove mode, keep all fillers otherwise filter them out
        ]

        # if in strip mode, all fillers were kept and can now be stripped from
        # beginning and/or end depending on requirements
        start = 0
        end = len(values)
        if self.parse_mode == "strip-leading" or self.parse_mode == "strip-both":
            start = 0
            while start < len(values) and values[start] == filler_value:
                start += 1
        
        if self.parse_mode == "strip-trailing" or self.parse_mode == "strip-both":
            end = len(values)
            while end > start and values[end - 1] == filler_value:
                end -= 1

        # the specified type of the stripped processed array elements is returned
        return self.type_annotation(values[start:end])

    @override
    def packing_preprocessor(self, field: typing.Iterable) -> tuple[Any, ...]:
        # coerce any iterables to tuple before serialization, so even ones that don't support
        # subscription such as "set" can still be converted to ordered array
        field = tuple(field)
        # If the array is not complete in terms of size, attempt
        # to add filler items
        if len(field) < self.length:
            if self.filler is BindanticUndefined:
                raise ValueError(f"'{self.__class__.__name__}' '{self.field_name}' must be of size {self.length} but is only {len(field)} elements long and no Filler value was specified.")
            
            # add filler
            field = field + ((
                self.element_field.type_annotation() if self.filler is FillDefaultConstructor else self.filler
            , ) * (self.length - len(field)))

        # generate struct elements for each array element and join them in one single tuple
        return sum((
            self.element_field.packing_preprocessor(field[i])
            for i in range(self.length)
        ), ())


ET = typing.TypeVar("ET")
ArrayList = Annotated[list[ET], ArrayField()]
ArrayTuple = Annotated[tuple[ET, ...], ArrayField()]
ArraySet = Annotated[set[ET], ArrayField()]
ArrayFrozenSet = Annotated[frozenset[ET], ArrayField()]
ArrayDeque = Annotated[deque[ET], ArrayField()]
