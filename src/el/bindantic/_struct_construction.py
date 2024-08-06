"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
06.08.24, 09:46
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Handling of Struct class creation similar to and extending Pydantic's model construction.
"""


import typing
from typing import Callable, Any, Optional, dataclass_transform
import dataclasses
from ._deps import pydantic, ModelMetaclass

if typing.TYPE_CHECKING:
    from ._base_struct import BaseStruct


PyStructBaseTypes = bytes | int | bool | float
StructIntermediate = typing.Collection[PyStructBaseTypes] | PyStructBaseTypes

BinaryDataType = typing.Literal[
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "int8",
    "int16",
    "int32",
    "int64",
    "float32",
    "float64",
    "char",
    "bool",
    "string",
    "bytes",
    "padding"
]

ARRAY_CAPABLE_TYPES: list[BinaryDataType] = [
    "uint8"
    "uint16"
    "uint32"
    "uint64"
    "int8"
    "int16"
    "int32"
    "int64"
    "float32"
    "float64"
    "char"
    "bool"
]


@dataclasses.dataclass(
    init=False, repr=True, eq=False, order=False,
    unsafe_hash=False, frozen=False, match_args=True,
    kw_only=False, slots=False, weakref_slot=False
)
class StructField:
    """
    Class for holding configuration and info for binary fields
    of the structure. Some info is only populated during class creating
    and other information can be passed directly by the user as field config.
    """

    # public fields to be provided by user

    # What binary datatype the field has
    binary_type: BinaryDataType
    
    # length for array
    length: Optional[int] = None
    
    # bit width for types where that makes sense. This defines how many bits are consumed,
    # somewhat like a C bit field
    #width: Optional[int] = None
    
    # the encoding used for strings
    encoding: str = "utf-8"

    def __post_init__(self) -> None:
        # the actual python datatype to represent this field
        self._type_annotation: type = ...

        # The code representing this field in a python struct string
        self._struct_code: str = ""

        # functions called after unpacking or before packing to convert the unpacked but 
        # raw structure variable (bytes | int | bool | float) to a different higher-level 
        # python object or the other way around.
        self._unpacking_postprocessor: Callable[[PyStructBaseTypes], Any] = lambda data: data
        self._packing_preprocessor: Callable[[Any], PyStructBaseTypes] = lambda field: field

        # whether this field is an outlet for a computed field, in which case
        # it will not be unpacked
        self._is_outlet = False

        # how many struct elements this field consumes or provides
        self._element_consumption: int = 1

        # how many bytes this field takes up in the structure
        self._bytes_consumption: int = 0

        # configure depending on the type
        match self.binary_type:
            
            case "uint8":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 1 * self.length
                self._struct_code = f"{self.length}B"
            
            case "uint16":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 2 * self.length
                self._struct_code = f"{self.length}H"
            
            case "uint32":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 4 * self.length
                self._struct_code = f"{self.length}I"
            
            case "uint64":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 8 * self.length
                self._struct_code = f"{self.length}Q"
            
            case "int8":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 1 * self.length
                self._struct_code = f"{self.length}b"
            
            case "int16":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 2 * self.length
                self._struct_code = f"{self.length}h"
            
            case "int32":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 4 * self.length
                self._struct_code = f"{self.length}i"
            
            case "int64":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 8 * self.length
                self._struct_code = f"{self.length}q"
            
            case "float32":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 4 * self.length
                self._struct_code = f"{self.length}f"
            
            case "float64":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 8 * self.length
                self._struct_code = f"{self.length}d"
            
            case "char":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 1 * self.length
                self._struct_code = f"{self.length}c"
            
            case "bool":
                if self.length is None:
                    self.length = 1
                self._bytes_consumption = 1 * self.length
                self._struct_code = f"{self.length}?"
            
            case "string":      # fixed length string (bytes converted to string)
                self._struct_code = f"{int(self.length)}s"
                self._unpacking_postprocessor = lambda data: data.decode(self.encoding)  # decode bytes to string
                self._packing_preprocessor = lambda field: field.encode(self.encoding)     # encode string to bytes
            
            case "bytes":       # fixed length byte array (not converted to string)
                self._struct_code = f"{int(self.length)}s"
            
            case "padding":     # fixed number of bytes that are ignored
                self._struct_code = f"{int(self.length)}x"

            case _: # TODO: figure out how to make this extendable 
                raise TypeError(f"Invalid binary type '{self.binary_type}")

        self._configure_struct_field()
    
    def _configure_struct_field(self) -> None:
        """
        To be overridden by base classes to hook into the configuration process
        after initialization
        """
        ...

    def _default_postprocessor(self, unpacked: PyStructBaseTypes):
        """
        By default, this simply returns the value from struct unpacking
        """
        return unpacked
    
    def _default_preprocessor(self, field_value: PyStructBaseTypes):
        """
        By default, this simply returns the field value directly
        """
        return field_value


# This decorator enables type hinting magic (https://stackoverflow.com/a/73988406)
# https://typing.readthedocs.io/en/latest/spec/dataclasses.html#dataclass-transform
# Technically this is undefined behavior because ModelMetaclass also has this: 
# https://typing.readthedocs.io/en/latest/spec/dataclasses.html#undefined-behavior
# But it is the only way this can be accomplished (at least in vscode)
@dataclass_transform(kw_only_default=True, field_specifiers=(pydantic.Field, pydantic.PrivateAttr))
class StructMetaclass(ModelMetaclass):
    def __new__(
        mcs, 
        cls_name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        """
        Metaclass for creating Bindantic structs (Pydantic models with
        additional binary structure support).

        Args:
            cls_name: The name of the class to be created.
            bases: The base classes of the class to be created.
            namespace: The attribute dictionary of the class to be created.
            **kwargs: Catch-all for any other keyword arguments.

        Returns:
            The new class created by the metaclass.
        """

        # This is the construction of Struct class itself which we don't want to do anything with
        if bases == (pydantic.BaseModel,):
            #print("Creating 'Struct' class")
            return super().__new__(mcs, cls_name, bases, namespace)
        
        # another class
        print(f"\nCreating struct subclass {cls_name}")
        #print(f"{mcs=}, {cls_name=}, {bases=}, {namespace=}")
        # run pydantic's ModelMetaclass' __new__ method to create a regular pydantic model
        # as well as do the heavy lifting of collecting fields and reading annotations.
        cls = super().__new__(mcs, cls_name, bases, namespace, **kwargs)

        # using cast() because normal type hinting didn't seem to be good enough for intellisense
        if typing.TYPE_CHECKING:
            cls = typing.cast(BaseStruct, cls)
        
        # collect dict of all binary structure fields
        cls.struct_fields = dict()
        for field_name, field in cls.model_fields.items():
            for meta_element in field.metadata:
                if isinstance(meta_element, StructField):   # struct field found
                    # if the field is an outlet, check that a corresponding
                    # computed field exists and use it's name instead
                    if field_name.endswith("_outlet"):
                        source_name = field_name.removesuffix("_outlet")
                        if source_name not in cls.model_computed_fields:    # sure there is a corresponding outlet
                            raise NameError(f"There is no computed field called '{source_name}' to to supply outlet '{field_name}'.")
                        meta_element._is_outlet = True  # mark this as an outlet
                        meta_element._type_annotation = field.annotation    # store the python type to use
                        cls.struct_fields[source_name] = meta_element
                    else:
                        cls.struct_fields[field_name] = meta_element
        
        cls.__bindantic_struct_code__ = ""

        for name, field in cls.struct_fields.items():
            # create structure string
            cls.__bindantic_struct_code__ += field._struct_code
        

            

        #inst.__signature__ = ClassAttribute(
        #    '__signature__',
        #    generate_pydantic_signature(init=inst.__init__, fields=model_fields, config_wrapper=config_wrapper),
        #)

        return cls
    

