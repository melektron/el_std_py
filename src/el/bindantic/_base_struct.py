"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
06.08.24, 09:44
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Base class of all structures which provides combined Pydantic Model and Binary Structure
functionality
"""

import typing
import struct
from typing import ClassVar
from ._deps import pydantic
from ._struct_construction import StructMetaclass, PyStructBaseTypes
from ._fields import BaseField
from ._config import StructConfigDict


class BaseStruct(pydantic.BaseModel, metaclass=StructMetaclass):
    """
    Pydantic BaseModel that also adds support for binary packing and unpacking
    """

    if typing.TYPE_CHECKING:
        # declarations of the fields that are dynamically added by the metaclass so they
        # are visible for intellisense.

        model_config: ClassVar[StructConfigDict]
        """
        Configuration for the struct, should be a dictionary conforming to [`StructConfigDict`][el.bindantic.StructConfigDict].
        This is an extension of pydantics ModelConfig
        """

        struct_fields: ClassVar[dict[str, BaseField]]
        """
        Metadata about the fields present inside the struct.
        This is a subset of Pydantic's model_fields since not all model
        fields are necessarily structure fields.

        mapping from field name to StructField instance
        """

        __bindantic_struct_code__: ClassVar[str]
        """
        String code representing the entire binary structure for the
        python struct module
        """

        __bindantic_struct_inst__: ClassVar[struct.Struct]
        """
        Compiled python structure instance used to pack and unpack from binary
        data.
        """

        __bindantic_element_consumption__: ClassVar[int]
        """
        How many structure primitives have to be passed to or
        are returned from the python structure library to
        represent this structure.
        """

        __bindantic_byte_consumption__: ClassVar[int]
        """
        Size of the structure in packed form in bytes
        """

    def __init__(self, /, **data: typing.Any) -> None:
        super().__init__(**data)
    
    def struct_dump_elements(self) -> tuple[PyStructBaseTypes, ...]:
        """
        Generates a tuple representing the structure, containing the smallest
        primitive values of the struct before they are converted to binary.
        These values are ready to be passed to struct.pack() for conversion to
        bytes.
        """
        # concatenate all the tuples of elements provided by the individual fields
        return sum((
            field.packing_preprocessor(getattr(self, name))
            for name, field
            in self.struct_fields.items()
        ), ())
    
    def struct_dump_bytes(self) -> bytes:
        """
        Packs the struct into its binary representation and
        returns a bytes object of corresponding size.
        """
        return self.__bindantic_struct_inst__.pack(
            *(self.struct_dump_elements())
        )

