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
from typing import Any, Annotated, override
from copy import deepcopy
from ._deps import pydantic
from ._field_config import *


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
        self.pydantic_field: pydantic.fields.FieldInfo | None = ...
        # the actual python datatype to represent this field
        self.type_annotation: type = ...
        # any annotation metadata passed via typing.Annotated
        self.annotation_metadata: list[Any] = ...

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

    def configure_struct_field(self, field_name: str, type_annotation: type, annotation_metadata: tuple[Any, ...], pydantic_field: pydantic.fields.FieldInfo | None) -> None:
        """
        Called during struct construction to configure the field with all
        additional information about it provided by pydantic
        """
        self.pydantic_field = pydantic_field
        self.type_annotation = type_annotation
        self.annotation_metadata = annotation_metadata

        # if this is a top level pydantic field we check for outlets
        if field_name.endswith("_outlet") and self.pydantic_field is not None:
            self.outlet_name = field_name
            self.field_name = field_name.removesuffix("_outlet")
            self.is_outlet = True
        else:
            self.field_name = field_name
        
        # read any field config items from metadata
        for meta_element in self.annotation_metadata:
            if isinstance(meta_element, FieldConfigItem):
                self.config_options.set_from_item(meta_element)
        
        # if the field is an outlet (and a top level field), disable most of it's 
        # pydantic functions, as those are covered by the corresponding computed field
        if self.is_outlet and self.pydantic_field is not None:
            self.pydantic_field.exclude = True
            self.pydantic_field.default = None
            self.pydantic_field.init = False

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
        return data
    
    def packing_preprocessor(self, field: Any) -> tuple[PyStructBaseTypes, ...]:         # Callable[[Any], PyStructBaseTypes] = lambda field: field
        """
        Function called before packing to convert a higher level python object
        into rawer types (bytes | int | bool | float) that can be packed into
        a structure.

        Can be overridden by subclasses to implement specialized behavior.
        """
        return (field, )


def get_field_from_type_data(
    field_name: str,
    type_annotation: type,
    annotation_metadata: tuple[Any, ...],
    pydantic_field: pydantic.fields.FieldInfo | None
) -> BaseField | None:
    """
    Processes the provided type information and metadata
    to extract and configure the appropriate structure
    field class instance to represent this field.
    If the field is a top-level field in a structure (e.g. not 
    an array element) the pydantic FieldInfo can optionally be
    provided so the pydantic config can be adjusted.
    """
    for meta_element in annotation_metadata:
        match meta_element:
            case BaseField():   # struct field found
                # deepcopy the instance from annotations so the provided config is 
                # kept but multiple fields with the same shortcut type-alias don't
                # share a single field instance
                struct_field = deepcopy(meta_element)
                # configure the field
                struct_field.configure_struct_field(
                    field_name, 
                    type_annotation,
                    annotation_metadata,
                    pydantic_field  # pass on the optional
                )
                
                return struct_field
    # TODO: add support for substructures
    return None # No metadata found to identify this as a struct field

class IntegerField(BaseField):
    def __init__(self, size: int, code: str, signed: bool) -> None:
        super().__init__()
        self.supported_py_types = (int, )
        self.bytes_consumption = size
        self.struct_code = code
        self.signed = signed

Uint8 = Annotated[int, IntegerField(1, "B", False)]
Uint16 = Annotated[int, IntegerField(2, "H", False)]
Uint32 = Annotated[int, IntegerField(4, "I", False)]
Uint64 = Annotated[int, IntegerField(8, "Q", False)]
Int8 = Annotated[int, IntegerField(1, "b", True)]
Int16 = Annotated[int, IntegerField(2, "h", True)]
Int32 = Annotated[int, IntegerField(4, "i", True)]
Int64 = Annotated[int, IntegerField(8, "q", True)]


class EnumField[ET: enum.Enum](IntegerField):
    """
    Integer converted to  (bytes converted to string)
    """
    def __init__(self, size: int, code: str, signed: bool) -> None:
        super().__init__(size, code, signed)
        self.supported_py_types = (enum.Enum, )

    # TODO: see if we can check with typevar
    #@override
    #def _type_check(self) -> None:
    #    return issubclass(self.type_annotation, enum.Enum)

    def unpacking_postprocessor(self, data: tuple[int, ...]) -> ET:
        return self.type_annotation(data[0])   # type_annotation should be the enum

    def packing_preprocessor(self, field: ET) -> tuple[int, ...]:
        return (field.value, )  # get numerical enum value

ET = typing.TypeVar("ET")

EnumU8 = Annotated[ET, EnumField[ET](1, "B", False)]
EnumU16 = Annotated[ET, EnumField[ET](2, "H", False)]
EnumU32 = Annotated[ET, EnumField[ET](4, "I", False)]
EnumU64 = Annotated[ET, EnumField[ET](8, "Q", False)]
Enum8 = Annotated[ET, EnumField[ET](1, "b", True)]
Enum16 = Annotated[ET, EnumField[ET](2, "h", True)]
Enum32 = Annotated[ET, EnumField[ET](4, "i", True)]
Enum64 = Annotated[ET, EnumField[ET](8, "q", True)]


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

Char = Annotated[str, CharField()]


class BoolField(BaseField):
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (bool, )
        self.bytes_consumption = 1
        self.struct_code = "?"

Bool = Annotated[bool, BoolField()]


class StringField(BaseField):
    """
    fixed length string (bytes converted to string)
    """
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (str, )

        self.length: int = ...
        self.encoding: str = ...
    
    @override
    def _configure_specialization(self) -> None:
        self.length = self.config_options.get_with_error(self, Len)
        self.encoding = self.config_options.get_with_error(self, Encoding, "utf-8")
        self.struct_code = f"{int(self.length)}s"
        self.bytes_consumption = self.length
        
    def unpacking_postprocessor(self, data: tuple[bytes, ...]) -> str:
        return data[0].decode(self.encoding[0])  # decode bytes to string

    def packing_preprocessor(self, field: str) -> tuple[bytes, ...]:
        return (field.encode(self.encoding), ) # encode string to bytes

String = Annotated[str, StringField()]


class BytesField(BaseField):
    """
    fixed length byte array (not converted to string)
    """
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (bytes, )

        self.length: int = ...
    
    @override
    def _configure_specialization(self) -> None:
        self.length = self.config_options.get_with_error(self, Len)
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
        self.length = self.config_options.get_with_error(self, Len)
        self.struct_code = f"{int(self.length)}x"
        self.bytes_consumption = self.length
        # padding bytes are not converted to any python objects
        self.element_consumption = 0

        # here this field could be disabled for pydantic but for now 
        # this is instead done in the padding annotation shortcut
        #if self.pydantic_field is not None:
        #    self.pydantic_field.exclude = True
        #    self.pydantic_field.default = None
        #    self.pydantic_field.init = False

Padding = Annotated[None, PaddingField(), pydantic.Field(exclude=True, default=None, init=False)]


class ArrayField[ET: BaseField](BaseField):
    """
    fixed length array of another binary capable type
    """
    def __init__(self) -> None:
        super().__init__()
        self.supported_py_types = (list, )
        
        self.element_field: ET = ...
    
    @override
    def _type_check(self) -> None:
        if not issubclass(typing.get_origin(self.type_annotation), self.supported_py_types):
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must resolve to one of {self.supported_py_types}, not '{typing.get_origin(self.type_annotation)}'")

        # extract and check the element type
        try:
            element_type_annotation = typing.get_args(self.type_annotation)[0]
        except KeyError:
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must be subscripted with an element type")
        
        try:
            assert issubclass(typing.get_origin(element_type_annotation), (Annotated, ))   # TODO: add support for substructures
            self.element_field = get_field_from_type_data(
                self.field_name + ".__element__",
                typing.get_args(element_type_annotation)[0],
                element_type_annotation.__metadata__,
                None    # not a top level struct field
            )
            assert self.element_field is not None
        except AssertionError:
            raise TypeError(f"'{self.__class__.__name__}' '{self.field_name}' must be subscripted with a binary-capable field type, not '{element_type_annotation}'")

        if isinstance(self.element_field, PaddingField):
            raise TypeError(f"Elements of '{self.__class__.__name__}' '{self.field_name}' should not be 'Padding'. Use Padding directly.")

    @override
    def _configure_specialization(self) -> None:
        self.length = self.config_options.get_with_error(self, Len)
        self.filler: Any | BindanticUndefinedType = self.config_options.get_with_error(self, Filler, BindanticUndefined)
        self.struct_code = "".join([self.element_field.struct_code] * self.length)
        self.bytes_consumption = self.length * self.element_field.bytes_consumption
        self.element_consumption = self.length * self.element_field.element_consumption
        
    def unpacking_postprocessor(self, data: tuple[PyStructBaseTypes, ...]) -> typing.Iterable:
        # split up struct elements for each array element and post-process them.
        # A list of all processed array elements is returned
        return self.type_annotation(    # should be an iterable type
            self.element_field.unpacking_postprocessor(
                data[   # pull out the amount of data elements consumed by the inner element type
                    (i * self.element_field.element_consumption) 
                    : 
                    ((i+1) * self.element_field.element_consumption)
                ]
            )
            for i in range(self.length)
        )

    def packing_preprocessor(self, field: typing.Iterable) -> tuple[Any, ...]:
        if len(field) < self.length:
            if self.filler is BindanticUndefined:
                raise ValueError(f"'{self.__class__.__name__}' '{self.field_name}' must be of size {self.length} but is only {len(field)} elements long and no Filler value was specified.")
            
            # add filler
            field = tuple(field) + ((
                self.element_field.type_annotation() if self.filler is FillDefault else self.filler
            , ) * (self.length - len(field)))

        # generate struct elements for each array element and join them in one single tuple
        return sum((
            self.element_field.packing_preprocessor(element)
            for element in field
        ), ())


ET = typing.TypeVar("ET")
Array = Annotated[list[ET], ArrayField[ET]()]
