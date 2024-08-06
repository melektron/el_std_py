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
from typing import ClassVar
from ._deps import pydantic
from ._struct_construction import StructMetaclass, StructField


class BaseStruct(pydantic.BaseModel, metaclass=StructMetaclass):
    """
    Pydantic BaseModel that also adds support for binary packing and unpacking
    """

    if typing.TYPE_CHECKING:
        # declarations of the fields that are dynamically added by the metaclass so they
        # are visible for intellisense.

        struct_fields: ClassVar[dict[str, StructField]]
        """
        Metadata about the fields present inside the struct.
        This is a subset of Pydantic's model_fields since not all model
        fields are necessarily structure fields.

        mapping from field name to StructField instance
        """
    
    def __init__(self, /, **data: typing.Any) -> None:
        super().__init__(**data)
        print(f"got config: {self.struct_fields}")
