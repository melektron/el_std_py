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
from copy import deepcopy
from ._deps import pydantic, ModelMetaclass

if typing.TYPE_CHECKING:
    from ._base_struct import BaseStruct
from ._fields import BaseField, get_field_from_type_data

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
            # deepcopy so config is kept but multiple fields with the same
            # shortcut type-alias don't share a single field instance
            struct_field = get_field_from_type_data(
                field_name, 
                field.annotation,
                field.metadata,
                field
            )
            if struct_field is None:    # not a struct field
                continue;
            # if the field is an outlet, check that a corresponding
            # computed field exists and use it's name instead
            if struct_field.is_outlet:
                if struct_field.field_name not in cls.model_computed_fields:
                    raise NameError(f"There is no computed field called '{struct_field.field_name}' to to supply outlet '{struct_field.outlet_name}'.")
            cls.struct_fields[struct_field.field_name] = struct_field
        
        cls.__bindantic_struct_code__ = ""

        for name, field in cls.struct_fields.items():
            # create structure string
            cls.__bindantic_struct_code__ += field.struct_code
        

            

        #inst.__signature__ = ClassAttribute(
        #    '__signature__',
        #    generate_pydantic_signature(init=inst.__init__, fields=model_fields, config_wrapper=config_wrapper),
        #)

        return cls
    
