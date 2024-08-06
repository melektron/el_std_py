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

FieldDataType = typing.Literal[
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
    "string",
    "padding"
]

class VStr:
    ...


@dataclasses.dataclass
class StructField:
    """
    Class for holding configuration and info for binary fields
    of the structure. Some info is only populated during class creating
    and other information can be passed directly by the user as field config.
    """

    # public fields to be provided by user

    # What binary datatype the field has
    binary_type: FieldDataType
    # length for types where that makes sense (array, string)
    length: Optional[int] = None
    # bit width for types where that makes sense. This defines how many bits are consumed,
    # somewhat like a C bit field
    width: Optional[int] = None

    def __post_init__(self) -> None:
        # The code representing this field in a python struct string
        self._struct_code: str = ""
        self._unpacking_postprocessor: Callable = self._default_postprocessor
        self._packing_preprocessor: Callable = self._default_preprocessor

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
# https://typing.readthedocs.io/en/latest/spec/dataclasses.html#dataclass-transform
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
        
        ann: dict[str, type] = namespace["__annotations__"]
        for name, annotation in ann.items():
            if typing.get_origin(annotation) is typing.Annotated:
                actual_type, *metadata = typing.get_args(annotation)
                if actual_type is VStr:
                    ann[name] = typing.Annotated[str, *metadata]
                    print("\n\n GOT VSTR! \n\n")


        # another class
        print("Creating struct subclass")
        #print(f"{mcs=}, {cls_name=}, {bases=}, {namespace=}")
        # run pydantic's ModelMetaclass' __new__ method to create a regular pydantic model
        # as well as do the heavy lifting of collecting fields and reading annotations.
        cls = super().__new__(mcs, cls_name, bases, namespace, **kwargs)

        # using cast() because normal type hinting didn't seem to be good enough for intellisense
        if typing.TYPE_CHECKING:
            cls = typing.cast(BaseStruct, cls)
        
        print(cls.model_computed_fields)
        
        # collect dict of all binary structure fields
        cls.struct_fields = dict()
        for field_name, field in cls.model_fields.items():
            print(f"{field_name}: {field.metadata}")
            for meta_element in field.metadata:
                if isinstance(meta_element, StructField):
                    # struct field found, save it
                    print(" -> Is Struct field")
                    cls.struct_fields[field_name] = meta_element
        
        for name, field in cls.struct_fields.items():
            print(f"{name}: {field}")

            

        #inst.__signature__ = ClassAttribute(
        #    '__signature__',
        #    generate_pydantic_signature(init=inst.__init__, fields=model_fields, config_wrapper=config_wrapper),
        #)

        return cls
    

