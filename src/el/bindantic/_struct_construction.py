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


import struct
import typing
from typing import Callable, Any, Optional, dataclass_transform
from copy import deepcopy
from ._deps import pydantic, ModelMetaclass
if typing.TYPE_CHECKING:
    from ._base_struct import BaseStruct
from ._fields import get_field_from_field_info, get_raw_field_field_info


PyStructBaseTypes = bytes | int | bool | float
StructIntermediate = typing.Collection[PyStructBaseTypes] | PyStructBaseTypes


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
            struct_field = get_field_from_field_info(
                field_name,
                field,
                True,
                [cls_name]
            )
            if struct_field is None:    # not a struct field
                continue
            # if the field is an outlet, check that a corresponding
            # computed field exists and use it's name instead
            if struct_field.is_outlet:
                cf = cls.model_computed_fields.get(struct_field.field_name)
                if cf is None:
                    raise NameError(f"There is no computed field called '{struct_field.field_name}' to to supply outlet '{struct_field.outlet_name}'.")
                # check that the return type of the computed field is correct
                return_pd_field = pydantic.fields.FieldInfo.from_annotation(cf.return_type)
                return_st_field = get_raw_field_field_info(return_pd_field)
                if return_st_field is None or not struct_field.is_equivalent(return_st_field):  # check if the field TYPES are equivalent
                    raise TypeError(f"Outlet source '{struct_field.field_name}' must return the same binary-capable field type as it's outlet, not '{cf.return_type}'")
            cls.struct_fields[struct_field.field_name] = struct_field
        
        # start struct string depending on byte order
        match cls.model_config.get("byte_order"):
            case "native-aligned":
                cls.__bindantic_struct_code__ = "@"
            case "native":
                cls.__bindantic_struct_code__ = "="
            case "little-endian":
                cls.__bindantic_struct_code__ = "<"
            case "big-endian":
                cls.__bindantic_struct_code__ = ">"
            case "network":
                cls.__bindantic_struct_code__ = "!"
            case _:
                cls.__bindantic_struct_code__ = "="

        cls.__bindantic_element_consumption__ = 0
        cls.__bindantic_byte_consumption__ = 0

        # collect all the fields to one single big struct
        for name, field in cls.struct_fields.items():
            # create structure string
            cls.__bindantic_struct_code__ += field.struct_code
            # count element and byte length
            cls.__bindantic_element_consumption__ += field.element_consumption
            cls.__bindantic_byte_consumption__ += field.bytes_consumption

        # create pre-compiled python structure
        cls.__bindantic_struct_inst__ = struct.Struct(
            cls.__bindantic_struct_code__
        )

        return cls
    
    def __len__(cls: "BaseStruct"):
        """
        Size of the struct in bytes, similar to C sizeof()
        """
        return cls.__bindantic_byte_consumption__

    def __bool__(self) -> bool:
        """
        To prevent __len__ for being called when checking truthiness
        """
        return True
    

