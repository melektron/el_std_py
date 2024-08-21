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
from ._config import StructConfigDict, StructPackingError
if typing.TYPE_CHECKING:
    from ._fields import BaseField


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
    
    def __len__(self):
        """
        Size of the struct in bytes, similar to C sizeof().
        This is equivalent to calling on the struct
        class itself.
        """
        return self.__bindantic_byte_consumption__
    
    def __bool__(self) -> bool:
        """
        To prevent __len__ for being called when checking truthiness
        """
        return True
    
    def struct_dump_elements(self) -> tuple[PyStructBaseTypes, ...]:
        """
        Generates a tuple representing the structure, containing the smallest
        primitive values of the struct before they are converted to binary.
        These values are ready to be passed to struct.pack() for conversion to
        bytes.
        """
        # concatenate all the tuples of elements provided by the individual fields
        try:
            return sum((
                field.packing_preprocessor(getattr(self, name))
                for name, field
                in self.struct_fields.items()
            ), ())
        except Exception as e:
            raise StructPackingError(str(e))
    
    def struct_dump_bytes(self) -> bytes:
        """
        Packs the struct into its binary representation and
        returns a bytes object of corresponding size.
        """
        try:
            return self.__bindantic_struct_inst__.pack(
                *(self.struct_dump_elements())
            )
        except Exception as e:
            if isinstance(e, StructPackingError):
                raise
            raise StructPackingError(str(e))

    @classmethod
    def _struct_postprocess_elements(cls, elements: tuple[PyStructBaseTypes, ...]) -> dict[str, typing.Any]:
        """
        Postprocesses the structure from the provided structure elements and returns
        the structure value dict ready for validation. 
        
        This is to be used internally to allow validating substructures
        in one go with their parent.

        Params:
            elements: the structure elements to load the data from
        
        Raises:
            Anything that fields raise
        
        Returns:
            the unpacked structure dict ready for validation
        """
        output_val_dict: dict[str, typing.Any] = {}

        # just-in-time import this to avoid import reference
        from ._fields import PaddingField

        # let all fields consume their elements
        element_offset: int = 0
        for name, field in cls.struct_fields.items():
            # padding doesn't consume any elements
            if isinstance(field, PaddingField):
                continue
            # consume elements
            field_elements = elements[element_offset : (element_offset + field.element_consumption)]
            element_offset += field.element_consumption
            # outlet fields consume elements but the data is not processed as it
            # is instead provided by computed fields
            if field.is_outlet:
                continue
            # preprocess the data into the desired python object
            output_val_dict[name] = field.unpacking_postprocessor(field_elements)
        
        return output_val_dict

    @classmethod
    def _struct_unpack_bytes(cls, data: bytes | bytearray) -> dict[str, typing.Any]:
        """
        Unpacks the structure from a byte buffer, postprocesses
        it and then returns the data in dict form.
        
        Internally this makes use of _struct_postprocess_elements() which
        is called after unpacking the structure from bytes
        
        Params:
            data: the binary representation of the structure
        
        Raises:
            StructPackingError containing any exception raised during unpacking and postprocessing
        
        Returns:
            the unpacked structure dict ready for validation
        """
        
        try:
            return cls._struct_postprocess_elements(
                cls.__bindantic_struct_inst__.unpack(data)
            )
        except Exception as e:
            if isinstance(e, (StructPackingError, pydantic.ValidationError)):
                raise   # substructures could cause such errors and they will be passed up directly
            raise StructPackingError(f"{e.__class__.__name__}: {str(e)}")
    
    @classmethod
    def struct_validate_elements(cls, elements: tuple[PyStructBaseTypes, ...]) -> typing.Self:
        """
        Postprocesses and then validates the structure from the provided
        structure elements. These are the elements that would be returned
        by struct.unpack(). 
        
        After the elements have been processed into their python types, they
        are validated by pydantic to apply all other higher level constraints.

        Params:
            elements: the structure elements to load the data from
        
        Raises:
            StructPackingError: if struct postprocessing fails
            pydantic.ValidationError: if pydantic validation fails
        
        Returns:
            the validated structure instance
        """
        try:
            dict_repr = cls._struct_postprocess_elements(elements)
        except Exception as e:
            if isinstance(e, (StructPackingError, pydantic.ValidationError)):
                raise   # substructures could cause such errors and they will be passed up directly
            raise StructPackingError(f"{e.__class__.__name__}: {str(e)}")
        
        return cls.model_validate(dict_repr)

    @classmethod
    def struct_validate_bytes(cls, data: bytes | bytearray) -> typing.Self:
        """
        Unpacks the structure from a byte buffer, postprocesses and validates
        it and then returns the new structure instance. 
        
        Internally this makes use of struct_validate_elements() which
        is called after unpacking the structure.
        
        Params:
            data: the binary representation of the structure
        
        Raises:
            StructPackingError: if struct postprocessing or unpacking fails
            pydantic.ValidationError: if pydantic validation fails
        
        Returns:
            the validated structure instance
        """
        
        try:
            return cls.model_validate(cls._struct_unpack_bytes(data))
        except struct.error as e:
            raise StructPackingError(str(e))


